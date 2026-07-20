"""v1 — Basic RAG baseline.

Fixed-size character chunks + dense retrieval placeholder + LLM answer stub.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.corpus import load_document_text, load_manifest


VERSION = "v1_basic_rag"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 0
TOP_K = 4


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    step = max(size - overlap, 1)
    return [text[i : i + size] for i in range(0, len(text), step)]


def _keyword_score(question: str, chunk: str) -> float:
    """Temporary stand-in until embeddings are wired."""
    q_terms = {t.lower() for t in question.split() if len(t) > 2}
    if not q_terms:
        return 0.0
    c_lower = chunk.lower()
    hits = sum(1 for t in q_terms if t in c_lower)
    return hits / len(q_terms)


@dataclass
class BasicRagPipeline:
    version: str = VERSION

    def answer(self, question: str) -> PipelineResult:
        started = time.perf_counter()
        scored: list[RetrievedChunk] = []

        for doc in load_manifest():
            text = load_document_text(doc["path"])
            for chunk in _chunk_text(text):
                score = _keyword_score(question, chunk)
                if score <= 0:
                    continue
                scored.append(
                    RetrievedChunk(
                        document_id=doc["document_id"],
                        path=doc["path"],
                        text=chunk,
                        score=score,
                        metadata={
                            "status": doc.get("status"),
                            "version": doc.get("version"),
                            "effective_date": doc.get("effective_date"),
                        },
                    )
                )

        scored.sort(key=lambda c: c.score, reverse=True)
        top = scored[:TOP_K]
        citations = list(dict.fromkeys(c.document_id for c in top))
        context = "\n\n---\n\n".join(c.text for c in top) if top else ""

        answer = (
            f"[v1 stub] Top context for: {question}\n\n{context[:1200]}"
            if context
            else f"[v1 stub] No chunks retrieved for: {question}"
        )

        latency_ms = (time.perf_counter() - started) * 1000
        return PipelineResult(
            version=self.version,
            question=question,
            answer=answer,
            citations=citations,
            retrieved_chunks=top,
            latency_ms=latency_ms,
            notes="Basic RAG: fixed chunks; keyword score placeholder for dense retrieval",
        )


def build_pipeline() -> BasicRagPipeline:
    return BasicRagPipeline()
