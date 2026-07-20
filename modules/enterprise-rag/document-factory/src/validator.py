"""Validate generated markdown against plans, sections, SKUs, and word counts."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from .config_loader import (
    corpus_root,
    ensure_data_dirs,
    load_company_config,
    load_generation_config,
)
from .exporters import content_hash, jaccard_similarity, normalize_text, word_count
from .models import DocumentPlan
from .planner import load_plans


def _heading_present(text: str, heading: str) -> bool:
    pattern = rf"(?im)^#{{1,3}}\s+{re.escape(heading)}\s*$"
    return re.search(pattern, text) is not None


def _known_product_codes(company: dict) -> set[str]:
    return {p["code"] for p in company.get("products") or []}


def _word_bounds(gen: dict, plan: DocumentPlan) -> tuple[int, int]:
    classes = gen.get("document_classes") or {}
    counts = gen.get("word_counts") or {}
    if plan.corpus == "scale":
        bounds = counts.get("scale") or {"min": 150, "max": 600}
    elif plan.document_type in (classes.get("operational") or []):
        bounds = counts.get("operational") or {"min": 200, "max": 900}
    else:
        bounds = counts.get("core") or {"min": 400, "max": 1500}
    return int(bounds.get("min", 0)), int(bounds.get("max", 10_000))


def validate_document(
    plan: DocumentPlan,
    text: str,
    *,
    known_skus: set[str] | None = None,
    gen: dict | None = None,
) -> list[str]:
    errors: list[str] = []
    body = normalize_text(text)
    gen = gen or load_generation_config()

    for key, value in plan.required_facts.items():
        needle = normalize_text(str(value))
        if needle and needle not in body:
            errors.append(f"missing required fact {key}={value!r}")

    if plan.status and normalize_text(plan.status) not in body:
        errors.append(f"missing status={plan.status!r}")
    if plan.version and normalize_text(plan.version) not in body:
        errors.append(f"missing version={plan.version!r}")

    for heading in plan.sections:
        if not _heading_present(text, heading):
            errors.append(f"missing section heading: {heading}")

    wc = word_count(text)
    lo, hi = _word_bounds(gen, plan)
    if wc < lo or wc > hi:
        errors.append(f"word_count {wc} outside [{lo}, {hi}]")

    if known_skus is not None:
        found = set(re.findall(r"\bNRG-[A-Z]{3}-\d{4}\b", text))
        unknown = found - known_skus
        if unknown:
            errors.append(f"unknown product codes introduced: {sorted(unknown)}")

    for eq in plan.evaluation_questions:
        answer = normalize_text(eq.expected_answer)
        # Soft check: require a distinctive substring (first token chunk) when answer is long
        if len(answer) <= 80:
            if answer and answer not in body:
                errors.append(f"expected answer missing for {eq.id}: {eq.expected_answer!r}")
        else:
            # For longer answers, require ~60% of tokens
            tokens = [t for t in answer.split() if len(t) > 2]
            if tokens:
                hits = sum(1 for t in tokens if t in body)
                if hits / len(tokens) < 0.6:
                    errors.append(f"expected answer poorly grounded for {eq.id}")

    return errors


def validate_corpus(corpus: str) -> dict[str, int]:
    ensure_data_dirs(corpus)
    root = corpus_root(corpus)
    plans = load_plans(corpus)
    gen = load_generation_config()
    company = load_company_config()
    known_skus = _known_product_codes(company)
    threshold = float(gen.get("duplicate_similarity_threshold") or 0.92)

    failures_dir = root / "failures"
    failures_dir.mkdir(parents=True, exist_ok=True)
    report_path = failures_dir / "validation-report.jsonl"

    passed = 0
    failed = 0
    missing = 0
    duplicates = 0
    seen_hashes: dict[str, str] = {}
    recent_texts: list[tuple[str, str]] = []  # (doc_id, text) last N for Jaccard

    with report_path.open("w", encoding="utf-8") as report:
        for plan in plans:
            path = root / plan.path
            if not path.exists():
                missing += 1
                report.write(
                    json.dumps(
                        {"document_id": plan.document_id, "path": plan.path, "errors": ["file missing"]}
                    )
                    + "\n"
                )
                continue

            text = path.read_text(encoding="utf-8")
            errors = validate_document(plan, text, known_skus=known_skus, gen=gen)

            digest = content_hash(text)
            if digest in seen_hashes:
                duplicates += 1
                errors.append(f"duplicate content hash of {seen_hashes[digest]}")
            else:
                seen_hashes[digest] = plan.document_id
                for other_id, other_text in recent_texts[-20:]:
                    if jaccard_similarity(text, other_text) >= threshold:
                        duplicates += 1
                        errors.append(f"near-duplicate of {other_id} (jaccard>={threshold})")
                        break
                recent_texts.append((plan.document_id, text))

            if errors:
                failed += 1
                dest = failures_dir / Path(plan.path).name
                shutil.copy2(path, dest)
                fail_meta = failures_dir / f"{plan.document_id}.validation.json"
                fail_meta.write_text(
                    json.dumps(
                        {"plan": plan.to_dict(), "errors": errors},
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                report.write(
                    json.dumps(
                        {"document_id": plan.document_id, "path": plan.path, "errors": errors}
                    )
                    + "\n"
                )
            else:
                passed += 1

    return {
        "planned": len(plans),
        "passed": passed,
        "failed": failed,
        "missing": missing,
        "duplicates": duplicates,
    }
