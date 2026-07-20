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
