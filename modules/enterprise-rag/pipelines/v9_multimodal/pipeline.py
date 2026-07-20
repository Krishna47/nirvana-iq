"""v9 — Multimodal RAG

Ingest images/tables/catalogs alongside text.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult


VERSION = "v9_multimodal"


@dataclass
class Pipeline:
    version: str = VERSION

    def answer(self, question: str) -> PipelineResult:
        return PipelineResult(
            version=self.version,
            question=question,
            answer=f"[{VERSION} stub] Not implemented yet. Ingest images/tables/catalogs alongside text.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
