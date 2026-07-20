"""Orchestrate planning, LLM generation, validation, and export."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from .config_loader import (
    CompanyConfig,
    GenerationConfig,
    load_system_prompt,
    load_type_prompt,
)
from .exporters import (
    FailureExporter,
    MarkdownExporter,
    relative_document_path,
    render_markdown_from_plan,
    write_json,
)
from .llm_client import LLMClient, LLMClientError
from .manifest import ManifestBuilder
from .models import DocumentPlan, GeneratedDocument, GenerationSummary
from .planner import DocumentPlanner
from .prose_renderer import render_document
from .validator import DocumentValidator

logger = logging.getLogger(__name__)


@dataclass
class GenerationCounters:
    generated: int = 0
    skipped: int = 0
    failed: int = 0
    started_at: float = field(default_factory=time.time)

    def estimate_completion(self, total: int) -> str:
        done = self.generated + self.skipped + self.failed
        if done == 0:
            return "n/a"
        elapsed = time.time() - self.started_at
        rate = done / elapsed if elapsed > 0 else 0.0
        remaining = max(total - done, 0)
        if rate <= 0:
            return "n/a"
        eta_seconds = remaining / rate
        eta = datetime.now(timezone.utc).timestamp() + eta_seconds
        return datetime.fromtimestamp(eta, tz=timezone.utc).isoformat()


class DocumentFactory:
    def __init__(
        self,
        company: CompanyConfig,
        generation: GenerationConfig,
        output_dir: Path,
        llm_client: LLMClient | None = None,
        concurrency: int | None = None,
        provider: str = "openai",
    ) -> None:
        self.company = company
        self.generation = generation
        self.output_dir = output_dir
        self.provider = provider
        self.planner = DocumentPlanner(company, generation)
        self.llm = llm_client or LLMClient(
            max_retries=generation.max_retries,
            base_delay_seconds=generation.retry_base_delay_seconds,
        )
        self.validator = DocumentValidator(
            known_product_codes=company.product_codes,
            similarity_threshold=generation.duplicate_similarity_threshold,
        )
        self.exporter = MarkdownExporter(output_dir)
        self.failures = FailureExporter(output_dir)
        self.manifest = ManifestBuilder(output_dir)
        self.concurrency = concurrency or generation.default_concurrency
        self._lock = Lock()
        self._normalized_corpus: list[str] = []
        self.system_prompt = load_system_prompt()

    def run(
        self,
        documents: int,
        start_year: int,
        end_year: int,
        seed: int,
        *,
        dry_run: bool = False,
        resume: bool = False,
    ) -> GenerationSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "raw").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "manifests").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "evaluation").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "failures").mkdir(parents=True, exist_ok=True)

        plans = self.planner.plan_documents(documents, start_year, end_year, seed)
        write_json(
            self.output_dir / "plans.json",
            [plan.model_dump(mode="json") for plan in plans],
        )

        counters = GenerationCounters()
        existing_ids = self.exporter.existing_document_ids() if resume else set()

        if dry_run:
            counters.generated = 0
            counters.skipped = 0
            summary = GenerationSummary(
                seed=seed,
                documents_requested=documents,
                generated=0,
                skipped=0,
                failed=0,
                start_year=start_year,
                end_year=end_year,
                output_dir=str(self.output_dir),
                dry_run=True,
                elapsed_seconds=time.time() - counters.started_at,
                estimated_completion=None,
            )
            # For dry-run, treat planned docs as "planned" and record counts clearly.
            summary.generated = len(plans)
            write_json(self.output_dir / "generation-summary.json", summary.model_dump(mode="json"))
            logger.info(
                "Dry run complete: planned=%s seed=%s years=%s-%s",
                len(plans),
                seed,
                start_year,
                end_year,
            )
            return summary

        if self.provider == "openai":
            self.llm.require_ready()
        work_plans = [plan for plan in plans if not (resume and plan.document_id in existing_ids)]
        skipped = len(plans) - len(work_plans)
        counters.skipped = skipped

        workers = 1 if self.provider == "local" else self.concurrency
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._generate_one, plan): plan for plan in work_plans
            }
            for future in as_completed(futures):
                plan = futures[future]
                try:
                    document = future.result()
                    if document is None:
                        counters.failed += 1
                    else:
                        counters.generated += 1
                except Exception as exc:  # noqa: BLE001 - surface unexpected worker errors
                    counters.failed += 1
                    self.failures.write_failure(plan, str(exc), None)
                    logger.exception("Unexpected failure for %s", plan.document_id)

                done = counters.generated + counters.skipped + counters.failed
                logger.info(
                    "Progress %s/%s | generated=%s skipped=%s failed=%s | eta=%s",
                    done,
                    len(plans),
                    counters.generated,
                    counters.skipped,
                    counters.failed,
                    counters.estimate_completion(len(plans)),
                )

        self.manifest.write()
        summary = GenerationSummary(
            seed=seed,
            documents_requested=documents,
            generated=counters.generated,
            skipped=counters.skipped,
            failed=counters.failed,
            start_year=start_year,
            end_year=end_year,
            output_dir=str(self.output_dir),
            dry_run=False,
            elapsed_seconds=round(time.time() - counters.started_at, 3),
            estimated_completion=counters.estimate_completion(len(plans)),
        )
        write_json(self.output_dir / "generation-summary.json", summary.model_dump(mode="json"))
        return summary

    def _generate_one(self, plan: DocumentPlan) -> GeneratedDocument | None:
        user_prompt = self._build_user_prompt(plan)
        raw_response: str | None = None
        try:
            if self.provider == "local":
                raw_response = render_document(plan)
            else:
                raw_response = self.llm.generate(self.system_prompt, user_prompt)
            markdown = render_markdown_from_plan(plan, raw_response)
            with self._lock:
                result = self.validator.validate(plan, markdown, self._normalized_corpus)
            if not result.ok:
                raise ValueError("; ".join(result.errors))

            document = GeneratedDocument(
                plan=plan,
                markdown=markdown,
                word_count=result.word_count,
                content_hash=result.content_hash,
                relative_path=relative_document_path(plan),
            )
            path = self.exporter.write_document(document)
            with self._lock:
                self._normalized_corpus.append(result.normalized_text)
                self.manifest.add_document(document, path)
            return document
        except (LLMClientError, ValueError, OSError) as exc:
            self.failures.write_failure(plan, str(exc), raw_response)
            logger.error("Failed %s: %s", plan.document_id, exc)
            return None

    def _build_user_prompt(self, plan: DocumentPlan) -> str:
        type_prompt = load_type_prompt(plan.document_type.value, plan.word_min, plan.word_max)
        facts_payload = {
            "immutable_metadata": {
                "document_id": plan.document_id,
                "title": plan.title,
                "document_type": plan.document_type.value,
                "department": plan.department,
                "region": plan.region,
                "version": plan.version,
                "status": plan.status,
                "confidentiality": plan.confidentiality,
                "owner": plan.owner,
                "effective_date": plan.effective_date,
                "expiry_date": plan.expiry_date,
                "published_date": plan.published_date,
                "year": plan.year,
                "product_codes": plan.product_codes,
                "suppliers": plan.suppliers,
                "systems": plan.systems,
                "keywords": plan.keywords,
            },
            "metrics": plan.metrics,
            "facts": plan.facts,
            "required_sections": plan.required_sections,
            "evaluation_questions": [q.model_dump(mode="json") for q in plan.evaluation_questions],
            "instructions": [
                "Preserve all immutable metadata and metrics exactly.",
                "Include every required section heading exactly as provided.",
                "Ensure each expected_answer appears verbatim in the document body.",
                "Stay within the target word count.",
            ],
        }
        return (
            f"{type_prompt}\n\n"
            "SOURCE OF TRUTH FACTS (JSON):\n"
            f"{json.dumps(facts_payload, indent=2)}\n"
        )
