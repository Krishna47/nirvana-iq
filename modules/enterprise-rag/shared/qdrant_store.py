"""Qdrant Cloud client helpers."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from .openai_client import EMBED_DIM
from .settings import collection_name, settings

HYBRID_VERSIONS = frozenset({"v3_hybrid_search"})
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "bm25"
BM25_MODEL = "Qdrant/bm25"
HYBRID_PREFETCH = 20


def is_hybrid_version(version: str) -> bool:
    return version in HYBRID_VERSIONS


def get_qdrant() -> QdrantClient:
    cfg = settings()
    return QdrantClient(url=cfg["qdrant_url"], api_key=cfg["qdrant_api_key"], timeout=120)


def ensure_collection(version: str, *, recreate: bool = False) -> str:
    client = get_qdrant()
    name = collection_name(version)
    exists = client.collection_exists(name)
    if exists and recreate:
        client.delete_collection(name)
        exists = False
    if not exists:
        if is_hybrid_version(version):
            client.create_collection(
                collection_name=name,
                vectors_config={
                    DENSE_VECTOR_NAME: qm.VectorParams(
                        size=EMBED_DIM,
                        distance=qm.Distance.COSINE,
                    )
                },
                sparse_vectors_config={
                    SPARSE_VECTOR_NAME: qm.SparseVectorParams(modifier=qm.Modifier.IDF)
                },
            )
        else:
            client.create_collection(
                collection_name=name,
                vectors_config=qm.VectorParams(size=EMBED_DIM, distance=qm.Distance.COSINE),
            )
    return name


def point_id(document_id: str, path: str, chunk_index: int) -> str:
    raw = f"{document_id}|{path}|{chunk_index}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest[:32]))


def upsert_points(
    version: str,
    *,
    vectors: list[list[float]],
    payloads: list[dict[str, Any]],
    ids: list[str],
) -> None:
    if not vectors:
        return
    if not (len(vectors) == len(payloads) == len(ids)):
        raise ValueError("vectors, payloads, and ids must be the same length")
    client = get_qdrant()
    name = collection_name(version)
    points = [
        qm.PointStruct(id=pid, vector=vector, payload=payload)
        for pid, vector, payload in zip(ids, vectors, payloads, strict=True)
    ]
    client.upsert(collection_name=name, points=points, wait=True)


def upsert_hybrid_points(
    version: str,
    *,
    dense_vectors: list[list[float]],
    texts: list[str],
    payloads: list[dict[str, Any]],
    ids: list[str],
) -> None:
    if not dense_vectors:
        return
    if not (len(dense_vectors) == len(texts) == len(payloads) == len(ids)):
        raise ValueError("dense_vectors, texts, payloads, and ids must be the same length")
    client = get_qdrant()
    name = collection_name(version)
    points = [
        qm.PointStruct(
            id=pid,
            vector={
                DENSE_VECTOR_NAME: dense,
                SPARSE_VECTOR_NAME: qm.Document(text=text, model=BM25_MODEL),
            },
            payload=payload,
        )
        for pid, dense, text, payload in zip(ids, dense_vectors, texts, payloads, strict=True)
    ]
    client.upsert(collection_name=name, points=points, wait=True)


def search(
    version: str,
    *,
    query_vector: list[float],
    top_k: int = 4,
) -> list[qm.ScoredPoint]:
    client = get_qdrant()
    name = collection_name(version)
    response = client.query_points(
        collection_name=name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return list(response.points)


def hybrid_search(
    version: str,
    *,
    query_text: str,
    query_vector: list[float],
    top_k: int = 4,
    prefetch_limit: int = HYBRID_PREFETCH,
) -> list[qm.ScoredPoint]:
    client = get_qdrant()
    name = collection_name(version)
    response = client.query_points(
        collection_name=name,
        prefetch=[
            qm.Prefetch(
                query=query_vector,
                using=DENSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
            qm.Prefetch(
                query=qm.Document(text=query_text, model=BM25_MODEL),
                using=SPARSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
        ],
        query=qm.FusionQuery(fusion=qm.Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )
    return list(response.points)
