"""v2 — Better chunking

Section-aware / heading splits with overlap.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import PipelineResult


VERSION = "v2_better_chunking"


@dataclass
class Pipeline:
    version: str = VERSION

    def answer(self, question: str) -> PipelineResult:
        return PipelineResult(
            version=self.version,
            question=question,
            answer=f"[{VERSION} stub] Not implemented yet. Section-aware / heading splits with overlap.",
            citations=[],
            retrieved_chunks=[],
            latency_ms=0.0,
            notes="Stub",
        )


def build_pipeline() -> Pipeline:
    return Pipeline()
