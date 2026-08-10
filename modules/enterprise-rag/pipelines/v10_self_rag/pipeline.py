"""v10 — Self-RAG

Self-reflect on retrieval/generation; refuse or retry.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult
from shared.conversation import ChatMessage


VERSION = "v10_self_rag"


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
            answer=f"[{VERSION} stub] Not implemented yet. Self-reflect on retrieval/generation; refuse or retry.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
            search_query=question,
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
