"""v8 — Agentic RAG

Retrieve, critique gaps, re-retrieve, then answer.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult


VERSION = "v8_agentic_rag"


@dataclass
class Pipeline:
    version: str = VERSION

    def answer(self, question: str) -> PipelineResult:
        return PipelineResult(
            version=self.version,
            question=question,
            answer=f"[{VERSION} stub] Not implemented yet. Retrieve, critique gaps, re-retrieve, then answer.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
