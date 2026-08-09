"""v2 — Better chunking.

Section-aware markdown chunks with overlap + dense Qdrant retrieval + OpenAI generation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.openai_client import chat_answer, embed_query
from shared.qdrant_store import search


VERSION = "v2_better_chunking"
TOP_K = 4


@dataclass
class BetterChunkingPipeline:
    version: str = VERSION
    top_k: int = TOP_K

    def answer(self, question: str) -> PipelineResult:
        started = time.perf_counter()
        query_vector = embed_query(question)
        hits = search(self.version, query_vector=query_vector, top_k=self.top_k)

        top: list[RetrievedChunk] = []
        for hit in hits:
            payload = hit.payload or {}
            top.append(
                RetrievedChunk(
                    document_id=str(payload.get("document_id") or ""),
                    path=str(payload.get("path") or ""),
                    text=str(payload.get("text") or ""),
                    score=float(hit.score or 0.0),
                    metadata={
                        "status": payload.get("status"),
                        "version": payload.get("doc_version"),
                        "effective_date": payload.get("effective_date"),
                        "expiry_date": payload.get("expiry_date"),
                        "region": payload.get("region"),
                        "chunk_index": payload.get("chunk_index"),
                    },
                )
            )

        citations = list(dict.fromkeys(c.document_id for c in top if c.document_id))
        context_blocks = []
        for chunk in top:
            context_blocks.append(
                f"document_id: {chunk.document_id}\n"
                f"path: {chunk.path}\n"
                f"status: {chunk.metadata.get('status')}\n"
                f"{chunk.text}"
            )
        context = "\n\n---\n\n".join(context_blocks)
        answer = (
            chat_answer(question=question, context=context, version=self.version)
            if context
            else "No relevant documents were retrieved from the gold corpus."
        )

        latency_ms = (time.perf_counter() - started) * 1000
        return PipelineResult(
            version=self.version,
            question=question,
            answer=answer,
            citations=citations,
            retrieved_chunks=top,
            latency_ms=latency_ms,
            notes="Section-aware H1-H3 chunks + 120-char overlap; dense Qdrant + OpenAI generate",
        )


def build_pipeline() -> BetterChunkingPipeline:
    return BetterChunkingPipeline()
