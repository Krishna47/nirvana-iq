"""v6 — Multi-query

Generate multiple queries, retrieve per query, merge results.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult
from shared.conversation import ChatMessage


VERSION = "v6_multi_query"


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
            answer=f"[{VERSION} stub] Not implemented yet. Generate multiple queries, retrieve per query, merge results.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
            search_query=question,
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
