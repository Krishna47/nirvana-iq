"""Load corpus manifest and golden evaluation questions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import CORPUS_ROOT, MANIFEST_JSONL_PATH, MANIFEST_PATH, QUESTIONS_PATH


def load_manifest(path: Path | None = None) -> list[dict[str, Any]]:
    """Load gold manifest from JSON array or JSONL."""
    if path is not None:
        target = path
        if target.suffix == ".jsonl":
            return _load_jsonl(target)
        with target.open(encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
            raise ValueError(f"Expected list manifest in {target}")

    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open(encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
    if MANIFEST_JSONL_PATH.exists():
        return _load_jsonl(MANIFEST_JSONL_PATH)
    raise FileNotFoundError(
        f"No gold manifest at {MANIFEST_PATH} or {MANIFEST_JSONL_PATH}. "
        "Run document-factory plan/generate/manifest for corpus gold."
    )


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_questions(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or QUESTIONS_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"No questions at {target}. Run: python -m src.cli questions "
            "(from modules/enterprise-rag/document-factory)"
        )
    with target.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_doc_path(relative_path: str) -> Path:
    """Manifest paths are relative to the gold corpus root."""
    return CORPUS_ROOT / relative_path


def load_document_text(relative_path: str) -> str:
    return resolve_doc_path(relative_path).read_text(encoding="utf-8")


def find_documents_by_id(
    document_id: str,
    *,
    status: str | None = None,
    version: str | None = None,
    document_type: str | None = None,
    include_text: bool = True,
) -> list[dict[str, Any]]:
    """Return manifest rows matching document_id (may be multiple versions)."""
    needle = document_id.strip()
    if not needle:
        return []

    matches: list[dict[str, Any]] = []
    for doc in load_manifest():
        if str(doc.get("document_id") or "") != needle:
            continue
        if status is not None and str(doc.get("status") or "") != status:
            continue
        if version is not None and str(doc.get("version") or "") != version:
            continue
        if document_type is not None and str(doc.get("document_type") or "") != document_type:
            continue

        row = {
            "document_id": doc.get("document_id"),
            "title": doc.get("title"),
            "document_type": doc.get("document_type"),
            "department": doc.get("department"),
            "region": doc.get("region"),
            "version": doc.get("version"),
            "status": doc.get("status"),
            "effective_date": doc.get("effective_date"),
            "expiry_date": doc.get("expiry_date"),
            "path": doc.get("path"),
            "trap_tag": doc.get("trap_tag"),
            "confidentiality": doc.get("confidentiality"),
        }
        if include_text:
            path = doc.get("path")
            if not path:
                row["text"] = ""
                row["error"] = "manifest row missing path"
            else:
                try:
                    row["text"] = load_document_text(str(path))
                except FileNotFoundError:
                    row["text"] = ""
                    row["error"] = f"file not found: {path}"
        matches.append(row)
    return matches
