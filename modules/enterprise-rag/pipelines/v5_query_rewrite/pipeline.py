"""v5 — Query rewrite

Rewrite / expand / HyDE before retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult
from shared.conversation import ChatMessage


VERSION = "v5_query_rewrite"


@dataclass
class Pipeline:
    version: str = VERSION

    def answer(
        self,
        question: str,
        *,
        history: list[ChatMessage] | None = None,
    ) -> PipelineResult:
        _ = history
        return PipelineResult(
            version=self.version,
            question=question,
            answer=f"[{VERSION} stub] Not implemented yet. Rewrite / expand / HyDE before retrieval.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
            search_query=question,
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
