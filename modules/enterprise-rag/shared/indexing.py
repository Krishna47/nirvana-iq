"""Index gold corpus chunks into Qdrant Cloud."""

from __future__ import annotations

from typing import Any, Iterator

from .corpus import load_document_text, load_manifest
from .openai_client import embed_texts
from .qdrant_store import ensure_collection, point_id, upsert_points

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 0
EMBED_BATCH = 64
UPSERT_BATCH = 64


def chunk_text(text: str, size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    step = max(size - overlap, 1)
    return [text[i : i + size] for i in range(0, len(text), step) if text[i : i + size].strip()]


def iter_chunks(
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    limit_docs: int | None = None,
) -> Iterator[dict[str, Any]]:
    docs = load_manifest()
    if limit_docs is not None:
        docs = docs[:limit_docs]
    for doc in docs:
        text = load_document_text(doc["path"])
        for index, chunk in enumerate(chunk_text(text, chunk_size, chunk_overlap)):
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
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    limit_docs: int | None = None,
) -> dict[str, Any]:
    collection = ensure_collection(version, recreate=recreate)
    pending_texts: list[str] = []
    pending_payloads: list[dict[str, Any]] = []
    pending_ids: list[str] = []
    total = 0

    def flush() -> None:
        nonlocal total, pending_texts, pending_payloads, pending_ids
        if not pending_texts:
            return
        vectors = embed_texts(pending_texts, batch_size=EMBED_BATCH)
        upsert_points(version, vectors=vectors, payloads=pending_payloads, ids=pending_ids)
        total += len(pending_texts)
        pending_texts, pending_payloads, pending_ids = [], [], []

    for row in iter_chunks(chunk_size=chunk_size, chunk_overlap=chunk_overlap, limit_docs=limit_docs):
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
    return {"collection": collection, "chunks": total, "version": version}
