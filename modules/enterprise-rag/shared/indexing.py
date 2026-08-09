"""Index gold corpus chunks into Qdrant Cloud."""

from __future__ import annotations

import re
from typing import Any, Iterator

from .corpus import load_document_text, load_manifest
from .openai_client import embed_texts
from .qdrant_store import (
    ensure_collection,
    is_hybrid_version,
    point_id,
    upsert_hybrid_points,
    upsert_points,
)

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 0
SECTION_CHUNK_SIZE = 800
SECTION_CHUNK_OVERLAP = 120
EMBED_BATCH = 64
UPSERT_BATCH = 64

_FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,3})\s+.+", re.MULTILINE)

# Version → (strategy, chunk_size, chunk_overlap)
_VERSION_CHUNKING: dict[str, tuple[str, int, int]] = {
    "v2_better_chunking": ("section", SECTION_CHUNK_SIZE, SECTION_CHUNK_OVERLAP),
    "v3_hybrid_search": ("section", SECTION_CHUNK_SIZE, SECTION_CHUNK_OVERLAP),
}


def chunk_text(text: str, size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    step = max(size - overlap, 1)
    return [text[i : i + size] for i in range(0, len(text), step) if text[i : i + size].strip()]


def strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1).lstrip("\n")


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Return (heading_line, section_body) pairs. Empty heading means preamble."""
    matches = list(_HEADING_RE.finditer(body))
    if not matches:
        return [("", body.strip())] if body.strip() else []

    sections: list[tuple[str, str]] = []
    preamble = body[: matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))

    for i, match in enumerate(matches):
        heading = match.group(0).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_body = body[start:end].strip()
        sections.append((heading, section_body))
    return sections


def chunk_markdown_sections(
    text: str,
    size: int = SECTION_CHUNK_SIZE,
    overlap: int = SECTION_CHUNK_OVERLAP,
) -> list[str]:
    """Heading-aware chunks with overlap inside oversized sections."""
    body = strip_frontmatter(text)
    chunks: list[str] = []
    for heading, section_body in _split_sections(body):
        if not heading and not section_body:
            continue
        if not section_body:
            chunks.append(heading)
            continue

        prefix = f"{heading}\n\n" if heading else ""
        # Budget for body so heading + body stay near size when possible.
        body_budget = max(size - len(prefix), 1) if prefix else size
        if len(section_body) <= body_budget:
            chunks.append(f"{prefix}{section_body}".strip())
            continue

        for piece in chunk_text(section_body, size=body_budget, overlap=overlap):
            chunks.append(f"{prefix}{piece}".strip())
    return chunks


def resolve_chunking(version: str) -> tuple[str, int, int]:
    return _VERSION_CHUNKING.get(version, ("fixed", DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP))


def iter_chunks(
    *,
    strategy: str = "fixed",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    limit_docs: int | None = None,
) -> Iterator[dict[str, Any]]:
    docs = load_manifest()
    if limit_docs is not None:
        docs = docs[:limit_docs]
    for doc in docs:
        text = load_document_text(doc["path"])
        if strategy == "section":
            pieces = chunk_markdown_sections(text, chunk_size, chunk_overlap)
        else:
            pieces = chunk_text(text, chunk_size, chunk_overlap)
        for index, chunk in enumerate(pieces):
            yield {
                "document_id": doc["document_id"],
                "path": doc["path"],
                "chunk_index": index,
                "text": chunk,
                "title": doc.get("title"),
                "document_type": doc.get("document_type"),
                "department": doc.get("department"),
                "region": doc.get("region"),
                "version": doc.get("version"),
                "status": doc.get("status"),
                "effective_date": doc.get("effective_date"),
                "expiry_date": doc.get("expiry_date"),
            }


def index_gold(
    version: str,
    *,
    recreate: bool = False,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    limit_docs: int | None = None,
) -> dict[str, Any]:
    strategy, default_size, default_overlap = resolve_chunking(version)
    size = default_size if chunk_size is None else chunk_size
    overlap = default_overlap if chunk_overlap is None else chunk_overlap

    collection = ensure_collection(version, recreate=recreate)
    hybrid = is_hybrid_version(version)
    pending_texts: list[str] = []
    pending_payloads: list[dict[str, Any]] = []
    pending_ids: list[str] = []
    total = 0

    def flush() -> None:
        nonlocal total, pending_texts, pending_payloads, pending_ids
        if not pending_texts:
            return
        vectors = embed_texts(pending_texts, batch_size=EMBED_BATCH)
        if hybrid:
            upsert_hybrid_points(
                version,
                dense_vectors=vectors,
                texts=pending_texts,
                payloads=pending_payloads,
                ids=pending_ids,
            )
        else:
            upsert_points(version, vectors=vectors, payloads=pending_payloads, ids=pending_ids)
        total += len(pending_texts)
        pending_texts, pending_payloads, pending_ids = [], [], []

    for row in iter_chunks(
        strategy=strategy,
        chunk_size=size,
        chunk_overlap=overlap,
        limit_docs=limit_docs,
    ):
        pending_ids.append(point_id(row["document_id"], row["path"], row["chunk_index"]))
        pending_texts.append(row["text"])
        pending_payloads.append(
            {
                "document_id": row["document_id"],
                "path": row["path"],
                "chunk_index": row["chunk_index"],
                "text": row["text"],
                "title": row.get("title"),
                "document_type": row.get("document_type"),
                "department": row.get("department"),
                "region": row.get("region"),
                "doc_version": row.get("version"),
                "status": row.get("status"),
                "effective_date": row.get("effective_date"),
                "expiry_date": row.get("expiry_date"),
            }
        )
        if len(pending_texts) >= UPSERT_BATCH:
            flush()
            print(f"indexed {total} chunks -> {collection}", flush=True)

    flush()
    return {
        "collection": collection,
        "chunks": total,
        "version": version,
        "strategy": strategy,
        "hybrid": hybrid,
        "chunk_size": size,
        "chunk_overlap": overlap,
    }
