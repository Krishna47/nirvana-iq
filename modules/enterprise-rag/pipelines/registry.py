"""Registry of RAG pipeline versions for CLI and evals."""

from __future__ import annotations

from typing import Callable

from shared.contracts import RagPipeline

from pipelines.v1_basic_rag import build_pipeline as build_v1
from pipelines.v2_better_chunking import build_pipeline as build_v2
from pipelines.v3_hybrid_search import build_pipeline as build_v3
from pipelines.v4_reranking import build_pipeline as build_v4
from pipelines.v5_query_rewrite import build_pipeline as build_v5
from pipelines.v6_multi_query import build_pipeline as build_v6
from pipelines.v7_metadata import build_pipeline as build_v7
from pipelines.v8_agentic_rag import build_pipeline as build_v8
from pipelines.v9_multimodal import build_pipeline as build_v9
from pipelines.v10_self_rag import build_pipeline as build_v10

BUILDERS: dict[str, Callable[[], RagPipeline]] = {
    "v1_basic_rag": build_v1,
    "v2_better_chunking": build_v2,
    "v3_hybrid_search": build_v3,
    "v4_reranking": build_v4,
    "v5_query_rewrite": build_v5,
    "v6_multi_query": build_v6,
    "v7_metadata": build_v7,
    "v8_agentic_rag": build_v8,
    "v9_multimodal": build_v9,
    "v10_self_rag": build_v10,
}


def list_versions() -> list[str]:
    return list(BUILDERS.keys())


def get_pipeline(version: str) -> RagPipeline:
    try:
        return BUILDERS[version]()
    except KeyError as exc:
        known = ", ".join(list_versions())
        raise SystemExit(f"Unknown version {version!r}. Known: {known}") from exc
