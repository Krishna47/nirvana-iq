"""v4 — Reranking.

Hybrid retrieve top-N from v3 collection, LLM listwise rerank to top-K, then generate.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.conversation import ChatMessage, condense_for_retrieval, normalize_history
from shared.openai_client import chat_answer, embed_query, rerank_chunks
from shared.qdrant_store import hybrid_search


VERSION = "v4_reranking"
RETRIEVE_VERSION = "v3_hybrid_search"
CANDIDATE_N = 20
TOP_K = 4


@dataclass
class RerankingPipeline:
    version: str = VERSION
    retrieve_version: str = RETRIEVE_VERSION
    candidate_n: int = CANDIDATE_N
    top_k: int = TOP_K

    def answer(
        self,
        question: str,
        *,
        history: list[ChatMessage] | None = None,
    ) -> PipelineResult:
        started = time.perf_counter()
        prior = normalize_history(history)
        search_query = condense_for_retrieval(question, prior)
        query_vector = embed_query(search_query)
        hits = hybrid_search(
            self.retrieve_version,
            query_text=search_query,
            query_vector=query_vector,
            top_k=self.candidate_n,
        )

        texts = [str((hit.payload or {}).get("text") or "") for hit in hits]
        order = rerank_chunks(question=search_query, texts=texts, top_k=self.top_k)
        ranked_hits = [hits[i] for i in order if 0 <= i < len(hits)]

        top: list[RetrievedChunk] = []
        for hit in ranked_hits:
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
            chat_answer(
                question=question,
                context=context,
                version=self.version,
                history=prior,
            )
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
            notes="Hybrid N=20 + LLM listwise rerank to K=4; shares v3 collection",
            search_query=search_query,
        )


def build_pipeline() -> RerankingPipeline:
    return RerankingPipeline()
