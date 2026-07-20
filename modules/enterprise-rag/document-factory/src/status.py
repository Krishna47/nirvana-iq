"""Corpus status helpers."""

from __future__ import annotations

from .config_loader import corpus_root, plans_path
from .planner import load_plans


def corpus_status(corpus: str) -> dict[str, int | str]:
    plan_file = plans_path(corpus)
    if not plan_file.exists():
        return {"corpus": corpus, "planned": 0, "written": 0, "missing": 0, "failed_errors": 0}

    plans = load_plans(corpus)
    root = corpus_root(corpus)
    written = 0
    missing = 0
    for plan in plans:
        if (root / plan.path).exists():
            written += 1
        else:
            missing += 1

    failures_dir = root / "failures"
    failed_errors = 0
    if failures_dir.exists():
        failed_errors = len(list(failures_dir.glob("*.error.txt")))

    report = failures_dir / "validation-report.jsonl"
    validation_rows = 0
    if report.exists():
        validation_rows = sum(1 for line in report.read_text(encoding="utf-8").splitlines() if line.strip())

    return {
        "corpus": corpus,
        "planned": len(plans),
        "written": written,
        "missing": missing,
        "generate_error_files": failed_errors,
        "validation_issue_rows": validation_rows,
    }
