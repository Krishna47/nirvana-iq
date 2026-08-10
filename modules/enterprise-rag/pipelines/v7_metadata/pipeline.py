"""v7 — Metadata filters.

Hybrid retrieve on shared v3 collection with Qdrant payload filters
(status / region / year) — interview fix for expired-policy traps.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.conversation import ChatMessage, condense_for_retrieval, normalize_history
from shared.metadata_filters import infer_metadata_filters
from shared.openai_client import chat_answer, embed_query
from shared.qdrant_store import hybrid_search


VERSION = "v7_metadata"
RETRIEVE_VERSION = "v3_hybrid_search"
TOP_K = 4


@dataclass
class MetadataFilterPipeline:
    version: str = VERSION
    retrieve_version: str = RETRIEVE_VERSION
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
        query_filter, applied_filters = infer_metadata_filters(search_query)
        query_vector = embed_query(search_query)
        hits = hybrid_search(
            self.retrieve_version,
            query_text=search_query,
            query_vector=query_vector,
            top_k=self.top_k,
            query_filter=query_filter,
        )

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
            notes="Hybrid retrieve on v3 + Qdrant metadata filters (status/region/year)",
            search_query=search_query,
            applied_filters=applied_filters,
        )


def build_pipeline() -> MetadataFilterPipeline:
    return MetadataFilterPipeline()
