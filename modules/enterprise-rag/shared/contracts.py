"""Shared answer/citations interface for every RAG pipeline version."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from .conversation import ChatMessage


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    path: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    """Uniform output so versions can be compared on the same scorecard."""

    version: str
    question: str
    answer: str
    citations: list[str]
    retrieved_chunks: list[RetrievedChunk]
    latency_ms: float
    notes: str = ""
    search_query: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RagPipeline(Protocol):
    version: str

    def answer(
        self,
        question: str,
        *,
        history: list[ChatMessage] | None = None,
    ) -> PipelineResult:
        """Run retrieve → (optional rewrite/rerank) → generate."""


def run_pipeline(
    pipeline: RagPipeline,
    question: str,
    *,
    history: list[ChatMessage] | None = None,
) -> PipelineResult:
    """Thin helper so eval runners stay version-agnostic."""
    return pipeline.answer(question, history=history)
