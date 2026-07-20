"""Export generated documents to Markdown and supporting artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from .models import DocumentPlan, EvaluationQuestion, GeneratedDocument, ManifestEntry


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def sha256_file_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_front_matter(plan: DocumentPlan) -> dict[str, Any]:
    return {
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
        "company": "Nirvana Retail Group",
    }


def render_markdown_from_plan(
    plan: DocumentPlan,
    body_markdown: str,
    *,
    ensure_front_matter: bool = True,
) -> str:
    """Assemble final Markdown, injecting canonical front matter if absent/rewriting it."""
    body = body_markdown.strip()
    match = FRONT_MATTER_RE.match(body)
    if match:
        body = match.group(2).strip()

    if ensure_front_matter:
        front = yaml.safe_dump(build_front_matter(plan), sort_keys=False, allow_unicode=True).strip()
        return f"---\n{front}\n---\n\n{body}\n"
    return f"{body}\n"


def relative_document_path(plan: DocumentPlan) -> str:
    filename = f"{plan.document_id.lower().replace('_', '-')}.md"
    return str(Path("raw") / str(plan.year) / plan.document_type.value / filename)


class MarkdownExporter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.raw_dir = output_dir / "raw"

    def write_document(self, document: GeneratedDocument) -> Path:
        rel = document.relative_path or relative_document_path(document.plan)
        path = self.output_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document.markdown, encoding="utf-8")
        return path

    def existing_document_ids(self) -> set[str]:
        ids: set[str] = set()
        if not self.raw_dir.exists():
            return ids
        for path in self.raw_dir.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"^document_id:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
            if match:
                ids.add(match.group(1).strip())
            else:
                ids.add(path.stem.upper())
        return ids


class FailureExporter:
    def __init__(self, output_dir: Path) -> None:
        self.failures_dir = output_dir / "failures"
        self.failures_dir.mkdir(parents=True, exist_ok=True)

    def write_failure(
        self,
        plan: DocumentPlan,
        error: str,
        raw_response: str | None = None,
    ) -> Path:
        payload = {
            "document_id": plan.document_id,
            "error": error,
            "plan": plan.model_dump(mode="json"),
            "raw_response": raw_response,
        }
        path = self.failures_dir / f"{plan.document_id}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_manifest_csv(path: Path, entries: list[ManifestEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ManifestEntry.model_fields.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            row = entry.model_dump(mode="json")
            row["product_codes"] = "|".join(entry.product_codes)
            row["keywords"] = "|".join(entry.keywords)
            writer.writerow(row)


def evaluation_payload(questions: list[EvaluationQuestion]) -> list[dict[str, Any]]:
    return [question.model_dump(mode="json") for question in questions]
