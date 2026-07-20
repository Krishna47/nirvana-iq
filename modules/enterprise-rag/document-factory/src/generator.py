"""LLM generation with resume, concurrency, and progress logging."""

from __future__ import annotations

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config_loader import FACTORY_ROOT, corpus_root, ensure_data_dirs, load_generation_config
from .exporters import write_generation_summary
from .llm_client import LLMClient, load_dotenv
from .models import DocumentPlan
from .planner import load_plans

logger = logging.getLogger(__name__)


def _render_prompt(template: str, plan: DocumentPlan) -> str:
    facts = "\n".join(f"- {k}: {v}" for k, v in plan.required_facts.items())
    sections = "\n".join(f"- {s}" for s in plan.sections)
    eval_block = ""
    if plan.evaluation_questions:
        lines = []
        for eq in plan.evaluation_questions:
            lines.append(
                f"- Q: {eq.question}\n  A (must appear in doc): {eq.expected_answer}"
            )
        eval_block = "\n".join(lines)
    return (
        template.replace("{{document_id}}", plan.document_id)
        .replace("{{title}}", plan.title)
        .replace("{{document_type}}", plan.document_type)
        .replace("{{department}}", plan.department)
        .replace("{{region}}", plan.region)
        .replace("{{version}}", plan.version)
        .replace("{{status}}", plan.status)
        .replace("{{effective_date}}", plan.effective_date or "")
        .replace("{{expiry_date}}", plan.expiry_date or "")
        .replace("{{confidentiality}}", plan.confidentiality)
        .replace("{{required_facts}}", facts)
        .replace("{{sections}}", sections)
        .replace("{{evaluation_questions}}", eval_block or "(none)")
    )


def _default_model(corpus: str) -> str:
    gen = load_generation_config()
    if corpus == "gold":
        env_key = (gen.get("gold_models") or {}).get("default_env", "OPENAI_GOLD_MODEL")
        default = (gen.get("gold_models") or {}).get("default", "gpt-4.1-mini")
    else:
        env_key = (gen.get("scale_models") or {}).get("default_env", "OPENAI_SCALE_MODEL")
        default = (gen.get("scale_models") or {}).get("default", "gpt-4.1-nano")
    return os.environ.get(env_key) or os.environ.get("OPENAI_MODEL") or default


def _format_eta(done: int, total: int, elapsed: float) -> str:
    if done <= 0 or elapsed <= 0:
        return "n/a"
    rate = done / elapsed
    remaining = max(total - done, 0)
    seconds = remaining / rate if rate else 0
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours}h{mins:02d}m"
    return f"{mins}m{secs:02d}s"


def generate_corpus(
    corpus: str,
    *,
    model: str | None = None,
    concurrency: int = 3,
    resume: bool = True,
    limit: int | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv(FACTORY_ROOT / ".env")
    ensure_data_dirs(corpus)
    plans = load_plans(corpus)
    if limit is not None:
        plans = plans[:limit]

    root = corpus_root(corpus)
    system = (FACTORY_ROOT / "prompts" / "system.txt").read_text(encoding="utf-8")
    user_template = (FACTORY_ROOT / "prompts" / "generate.txt").read_text(encoding="utf-8")

    pending: list[DocumentPlan] = []
    skipped = 0
    for plan in plans:
        out_path = root / plan.path
        if resume and out_path.exists() and out_path.stat().st_size > 0:
            skipped += 1
            continue
        pending.append(plan)

    if dry_run:
        summary = {
            "planned": len(plans),
            "pending": len(pending),
            "skipped": skipped,
            "written": 0,
            "failed": 0,
        }
        write_generation_summary(corpus, **summary)
        return summary

    client = LLMClient(model=model or _default_model(corpus))
    gen_cfg = load_generation_config()
    max_retries = int(gen_cfg.get("max_retries") or 3)
    base_delay = float(gen_cfg.get("retry_base_delay_seconds") or 1.5)

    written = 0
    failed = 0
    failures_dir = root / "failures"
    failures_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    total_pending = len(pending)
    completed = 0

    def _one(plan: DocumentPlan) -> tuple[str, bool, str]:
        user = _render_prompt(user_template, plan)
        raw_response = ""
        try:
            raw_response = client.complete(
                system, user, max_retries=max_retries, base_delay=base_delay
            )
            out_path = root / plan.path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(raw_response.rstrip() + "\n", encoding="utf-8")
            return plan.document_id, True, ""
        except Exception as exc:  # noqa: BLE001
            payload = {
                "plan": plan.to_dict(),
                "error": str(exc),
                "raw_model_response": raw_response or None,
            }
            err_path = failures_dir / f"{plan.document_id}.failure.json"
            err_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            return plan.document_id, False, str(exc)

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        futures = [pool.submit(_one, plan) for plan in pending]
        for fut in as_completed(futures):
            doc_id, ok, err = fut.result()
            completed += 1
            if ok:
                written += 1
            else:
                failed += 1
                logger.warning("failed %s: %s", doc_id, err)
            elapsed = time.perf_counter() - started
            eta = _format_eta(completed, total_pending, elapsed)
            logger.info(
                "progress corpus=%s generated=%s skipped=%s failed=%s pending_done=%s/%s eta=%s",
                corpus,
                written,
                skipped,
                failed,
                completed,
                total_pending,
                eta,
            )

    summary = {
        "planned": len(plans),
        "pending": len(pending),
        "skipped": skipped,
        "written": written,
        "failed": failed,
    }
    write_generation_summary(corpus, **summary)
    return summary
