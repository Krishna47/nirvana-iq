"""Export manifests, CSV, generation summaries, and markdown helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config_loader import corpus_root
from .models import DocumentPlan, ManifestRecord


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def jaccard_similarity(a: str, b: str) -> float:
    """Token Jaccard over normalized text — used for near-duplicate detection."""
    ta = set(normalize_text(a).split())
    tb = set(normalize_text(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def render_front_matter(plan: DocumentPlan) -> str:
    lines = [
        "---",
        f"document_id: {plan.document_id}",
        f"title: {plan.title}",
        f"document_type: {plan.document_type}",
        f"department: {plan.department}",
        f"region: {plan.region}",
        f"version: {plan.version}",
        f"status: {plan.status}",
        f"effective_date: {plan.effective_date}",
        f"expiry_date: {plan.expiry_date}",
        f"confidentiality: {plan.confidentiality}",
        "---",
        "",
    ]
    return "\n".join(lines)


def write_csv_manifest(records: list[ManifestRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "document_id",
        "title",
        "document_type",
        "department",
        "region",
        "version",
        "status",
        "effective_date",
        "expiry_date",
        "path",
        "sha256",
        "trap_tag",
        "confidentiality",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {k: record.to_dict().get(k, "") for k in fieldnames}
            writer.writerow(row)


def write_generation_summary(
    corpus: str,
    *,
    planned: int,
    written: int,
    skipped: int,
    failed: int,
    pending: int | None = None,
    validated_passed: int | None = None,
    validated_failed: int | None = None,
    duplicates: int | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    root = corpus_root(corpus)
    out = root / "generation-summary.json"
    payload: dict[str, Any] = {
        "corpus": corpus,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "planned": planned,
        "pending": pending,
        "written": written,
        "skipped": skipped,
        "failed": failed,
        "validated_passed": validated_passed,
        "validated_failed": validated_failed,
        "duplicates": duplicates,
    }
    if extra:
        payload.update(extra)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
