"""v6 — Multi-query fusion.

LlamaIndex expands queries → hybrid retrieve each on v3 → client RRF → generate.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.conversation import ChatMessage, condense_for_retrieval, normalize_history
from shared.llamaindex_rewrite import expand_queries
from shared.openai_client import chat_answer, embed_query
from shared.qdrant_store import hybrid_search
from shared.retrieval_fusion import rrf_fuse


VERSION = "v6_multi_query"
RETRIEVE_VERSION = "v3_hybrid_search"
NUM_QUERIES = 3
PER_QUERY_K = 8
TOP_K = 4


@dataclass
class MultiQueryPipeline:
    version: str = VERSION
    retrieve_version: str = RETRIEVE_VERSION
    num_queries: int = NUM_QUERIES
    per_query_k: int = PER_QUERY_K
    top_k: int = TOP_K

    def answer(
        self,
        question: str,
        *,
        history: list[ChatMessage] | None = None,
    ) -> PipelineResult:
        started = time.perf_counter()
        prior = normalize_history(history)
        base = condense_for_retrieval(question, prior)
        queries = expand_queries(base, n=self.num_queries)

        ranked_lists = []
        for q in queries:
            query_vector = embed_query(q)
            hits = hybrid_search(
                self.retrieve_version,
                query_text=q,
                query_vector=query_vector,
                top_k=self.per_query_k,
            )
            ranked_lists.append(hits)

        fused = rrf_fuse(ranked_lists, top_k=self.top_k)

        top: list[RetrievedChunk] = []
        for hit in fused:
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
        search_query = " | ".join(queries)
        return PipelineResult(
            version=self.version,
            question=question,
            answer=answer,
            citations=citations,
            retrieved_chunks=top,
            latency_ms=latency_ms,
            notes="LlamaIndex multi-query expand → hybrid per query → client RRF → generate",
            search_query=search_query,
            search_queries=queries,
        )


def build_pipeline() -> MultiQueryPipeline:
    return MultiQueryPipeline()
