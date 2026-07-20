"""v7 — Metadata filters

Filter by status, dates, region (expired policy trap).
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult


VERSION = "v7_metadata"


@dataclass
class Pipeline:
    version: str = VERSION

    def answer(self, question: str) -> PipelineResult:
        return PipelineResult(
            version=self.version,
            question=question,
            answer=f"[{VERSION} stub] Not implemented yet. Filter by status, dates, region (expired policy trap).",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
