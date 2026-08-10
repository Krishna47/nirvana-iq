"""LangGraph retrieve → check → re-retrieve → generate for v8."""

from __future__ import annotations

import json
import operator
import re
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from shared.conversation import ChatMessage
from shared.metadata_filters import infer_metadata_filters
from shared.openai_client import chat_answer, embed_query, get_openai
from shared.qdrant_store import hybrid_search
from shared.settings import settings

RETRIEVE_VERSION = "v3_hybrid_search"
MAX_ROUNDS = 2
PER_ROUND_K = 4
FINAL_TOP_K = 6
VERSION = "v8_agentic_rag"

_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")


class AgentState(TypedDict, total=False):
    question: str
    history: list[ChatMessage]
    search_query: str
    followup_query: str
    round: int
    chunks: list[dict[str, Any]]
    applied_filters: dict[str, Any]
    agent_steps: Annotated[list[dict[str, Any]], operator.add]
    search_queries: Annotated[list[str], operator.add]
    sufficient: bool
    answer: str


def _chunk_key(chunk: dict[str, Any]) -> tuple[str, str, Any]:
    return (
        str(chunk.get("document_id") or ""),
        str(chunk.get("path") or ""),
        chunk.get("metadata", {}).get("chunk_index"),
    )


def _hits_to_chunks(hits: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for hit in hits:
        payload = hit.payload or {}
        out.append(
            {
                "document_id": str(payload.get("document_id") or ""),
                "path": str(payload.get("path") or ""),
                "text": str(payload.get("text") or ""),
                "score": float(hit.score or 0.0),
                "metadata": {
                    "status": payload.get("status"),
                    "version": payload.get("doc_version"),
                    "effective_date": payload.get("effective_date"),
                    "expiry_date": payload.get("expiry_date"),
                    "region": payload.get("region"),
                    "chunk_index": payload.get("chunk_index"),
                },
            }
        )
    return out


def _merge_chunks(
    existing: list[dict[str, Any]],
    new_chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, Any], dict[str, Any]] = {}
    for chunk in [*existing, *new_chunks]:
        key = _chunk_key(chunk)
        prev = by_key.get(key)
        if prev is None or float(chunk.get("score") or 0) > float(prev.get("score") or 0):
            by_key[key] = chunk
    merged = sorted(by_key.values(), key=lambda c: float(c.get("score") or 0), reverse=True)
    return merged[:FINAL_TOP_K]


def _context_from_chunks(chunks: list[dict[str, Any]]) -> str:
    blocks = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        blocks.append(
            f"document_id: {chunk.get('document_id')}\n"
            f"path: {chunk.get('path')}\n"
            f"status: {meta.get('status')}\n"
            f"{chunk.get('text') or ''}"
        )
    return "\n\n---\n\n".join(blocks)


def retrieve_node(state: AgentState) -> dict[str, Any]:
    round_num = int(state.get("round") or 0) + 1
    followup = (state.get("followup_query") or "").strip()
    base_query = (state.get("search_query") or state.get("question") or "").strip()
    query = followup if round_num > 1 and followup else base_query
    query_filter, applied = infer_metadata_filters(query)
    query_vector = embed_query(query)
    hits = hybrid_search(
        RETRIEVE_VERSION,
        query_text=query,
        query_vector=query_vector,
        top_k=PER_ROUND_K,
        query_filter=query_filter,
    )
    new_chunks = _hits_to_chunks(hits)
    merged = _merge_chunks(list(state.get("chunks") or []), new_chunks)
    step = {
        "type": "retrieve",
        "round": round_num,
        "search_query": query,
        "applied_filters": applied,
        "n_hits": len(new_chunks),
    }
    return {
        "round": round_num,
        "search_query": query,
        "chunks": merged,
        "applied_filters": applied,
        "search_queries": [query],
        "agent_steps": [step],
        "sufficient": False,
    }


def check_node(state: AgentState) -> dict[str, Any]:
    question = state.get("question") or ""
    chunks = list(state.get("chunks") or [])
    snippets = []
    for i, chunk in enumerate(chunks[:FINAL_TOP_K], start=1):
        text = (chunk.get("text") or "")[:400]
        snippets.append(
            f"[{i}] {chunk.get('document_id')} status={chunk.get('metadata', {}).get('status')}\n{text}"
        )
    context_preview = "\n\n".join(snippets) if snippets else "(no chunks)"

    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You grade whether retrieved context is sufficient to fully answer a Nirvana Retail "
        "Group knowledge question. Focus on coverage of distinct causes/facts (multi-hop), "
        "not writing style. Return ONLY JSON with keys: "
        'sufficient (bool), reason (string), followup_query (string). '
        "If insufficient, followup_query must be a focused standalone search query for the "
        "missing angle. If sufficient, followup_query must be an empty string."
    )
    user = (
        f"Question:\n{question}\n\nRetrieved context snippets:\n{context_preview}\n\nJSON:"
    )
    sufficient = True
    reason = "Context appears sufficient."
    followup_query = ""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        raw = (response.choices[0].message.content or "").strip()
        parsed: dict[str, Any] | None = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            match = _JSON_OBJECT_RE.search(raw)
            if match:
                parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            sufficient = bool(parsed.get("sufficient"))
            reason = str(parsed.get("reason") or reason)
            followup_query = str(parsed.get("followup_query") or "").strip()
            if sufficient:
                followup_query = ""
    except Exception:
        sufficient = True
        reason = "Sufficiency check failed open; proceeding to generate."
        followup_query = ""

    step = {
        "type": "check",
        "round": int(state.get("round") or 1),
        "sufficient": sufficient,
        "reason": reason,
        "followup_query": followup_query,
    }
    return {
        "sufficient": sufficient,
        "followup_query": followup_query,
        "agent_steps": [step],
    }


def generate_node(state: AgentState) -> dict[str, Any]:
    chunks = list(state.get("chunks") or [])
    context = _context_from_chunks(chunks)
    answer = (
        chat_answer(
            question=state.get("question") or "",
            context=context,
            version=VERSION,
            history=list(state.get("history") or []),
        )
        if context
        else "No relevant documents were retrieved from the gold corpus."
    )
    step = {
        "type": "generate",
        "round": int(state.get("round") or 0),
        "n_chunks": len(chunks),
    }
    return {"answer": answer, "agent_steps": [step]}


def _route_after_retrieve(state: AgentState) -> Literal["check", "generate"]:
    if int(state.get("round") or 0) >= MAX_ROUNDS:
        return "generate"
    return "check"


def _route_after_check(state: AgentState) -> Literal["retrieve", "generate"]:
    if state.get("sufficient"):
        return "generate"
    if int(state.get("round") or 0) >= MAX_ROUNDS:
        return "generate"
    if not (state.get("followup_query") or "").strip():
        return "generate"
    return "retrieve"


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("check", check_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges(
        "retrieve",
        _route_after_retrieve,
        {"check": "check", "generate": "generate"},
    )
    graph.add_conditional_edges(
        "check",
        _route_after_check,
        {"retrieve": "retrieve", "generate": "generate"},
    )
    graph.add_edge("generate", END)
    return graph.compile()


_COMPILED = None


def get_agent_graph():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = build_agent_graph()
    return _COMPILED
