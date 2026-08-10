"""LlamaIndex-backed query rewrite / expand for v5+ (keep out of v1–v4 import paths)."""

from __future__ import annotations

import json
import re

from .settings import settings

_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


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


def expand_queries(query: str, *, n: int = 3) -> list[str]:
    """Generate n diverse standalone search queries (includes the input query)."""
    q = (query or "").strip()
    if not q:
        return []
    n = max(1, n)

    def _finalize(candidates: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for text in [q, *candidates]:
            cleaned = (text or "").strip()
            if not cleaned:
                continue
            key = cleaned.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(cleaned)
            if len(out) >= n:
                break
        while len(out) < n:
            out.append(q)
        return out[:n]

    cfg = settings()
    try:
        from llama_index.llms.openai import OpenAI

        llm = OpenAI(
            model=cfg["openai_chat_model"],
            api_key=cfg["openai_api_key"],
            temperature=0.0,
        )
        prompt = (
            "You expand one user question into diverse standalone search queries for a "
            "retail enterprise RAG corpus (Nirvana Retail Group policies, reports, catalogs).\n"
            f"Return ONLY a JSON array of exactly {n} strings. No prose.\n"
            "Stay on the same topic as the user question. Do not invent unrelated topics "
            "(e.g. do not add promotions/SKUs unless the question is about them).\n"
            "Vary phrasing/angles within that topic only.\n"
            "Preserve exact SKUs, document IDs, and codes when present.\n"
            "This demo corpus is centered on 2025–2026; if year is omitted, prefer 2026.\n\n"
            f"User question:\n{q}\n\nJSON array:"
        )
        response = llm.complete(prompt)
        raw = (response.text or "").strip()
        candidates: list[str] = []
        for blob in (raw,):
            try:
                parsed = json.loads(blob)
            except json.JSONDecodeError:
                match = _JSON_ARRAY_RE.search(blob)
                if not match:
                    continue
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    continue
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, str) and item.strip():
                        candidates.append(item.strip())
                break
        return _finalize(candidates)
    except Exception:
        return _finalize([])
