"""LlamaIndex-backed query rewrite for v5+ (keep out of v1–v4 import paths)."""

from __future__ import annotations

from .settings import settings


def rewrite_for_retrieval(query: str) -> str:
    """Expand/clarify a question into a keyword-rich standalone search query."""
    q = (query or "").strip()
    if not q:
        return q

    cfg = settings()
    try:
        from llama_index.llms.openai import OpenAI

        llm = OpenAI(
            model=cfg["openai_chat_model"],
            api_key=cfg["openai_api_key"],
            temperature=0.0,
        )
        prompt = (
            "You rewrite user questions into standalone search queries for a retail "
            "enterprise RAG corpus (Nirvana Retail Group policies, reports, catalogs).\n"
            "Expand vague phrasing into clear keywords (region, product, policy topic, dates).\n"
            "Preserve exact SKUs, document IDs, and codes when present.\n"
            "This demo corpus is centered on 2025–2026; if the user says Q1/promo without a year, "
            "prefer 2026 (not older years).\n"
            "Return ONLY the search query text — no quotes, labels, or explanation.\n\n"
            f"User question:\n{q}\n\nStandalone search query:"
        )
        response = llm.complete(prompt)
        rewritten = (response.text or "").strip()
        if len(rewritten) >= 2 and rewritten[0] == rewritten[-1] and rewritten[0] in "\"'":
            rewritten = rewritten[1:-1].strip()
        return rewritten or q
    except Exception:
        return q
