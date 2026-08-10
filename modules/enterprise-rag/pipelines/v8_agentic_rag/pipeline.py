"""v8 — Agentic RAG.

LangGraph retrieve → sufficiency check → re-retrieve → generate,
on shared v3 hybrid with v7 metadata filters.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from shared.contracts import PipelineResult, RetrievedChunk
from shared.conversation import ChatMessage, condense_for_retrieval, normalize_history

from .graph import VERSION, get_agent_graph


@dataclass
class AgenticRagPipeline:
    version: str = VERSION

    def answer(
        self,
        question: str,
        *,
        history: list[ChatMessage] | None = None,
    ) -> PipelineResult:
        started = time.perf_counter()
        prior = normalize_history(history)
        search_query = condense_for_retrieval(question, prior)

        graph = get_agent_graph()
        final = graph.invoke(
            {
                "question": question,
                "history": prior,
                "search_query": search_query,
                "round": 0,
                "chunks": [],
                "applied_filters": {},
                "agent_steps": [],
                "search_queries": [],
                "sufficient": False,
                "followup_query": "",
                "answer": "",
            }
        )

        raw_chunks = list(final.get("chunks") or [])
        top = [
            RetrievedChunk(
                document_id=str(c.get("document_id") or ""),
                path=str(c.get("path") or ""),
                text=str(c.get("text") or ""),
                score=float(c.get("score") or 0.0),
                metadata=dict(c.get("metadata") or {}),
            )
            for c in raw_chunks
        ]
        citations = list(dict.fromkeys(c.document_id for c in top if c.document_id))
        search_queries = list(final.get("search_queries") or [])
        latency_ms = (time.perf_counter() - started) * 1000

        return PipelineResult(
            version=self.version,
            question=question,
            answer=str(final.get("answer") or ""),
            citations=citations,
            retrieved_chunks=top,
            latency_ms=latency_ms,
            notes=(
                "LangGraph retrieve→check→re-retrieve on v3 hybrid "
                "+ v7 metadata filters; max 2 retrieve rounds"
            ),
            search_query=" | ".join(search_queries) if search_queries else search_query,
            search_queries=search_queries,
            applied_filters=dict(final.get("applied_filters") or {}),
            agent_steps=list(final.get("agent_steps") or []),
        )


def build_pipeline() -> AgenticRagPipeline:
    return AgenticRagPipeline()
