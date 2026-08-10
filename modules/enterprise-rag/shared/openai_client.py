"""OpenAI embeddings and chat helpers (no LangChain)."""

from __future__ import annotations

import json
import re

from openai import OpenAI

from .settings import settings

# text-embedding-3-small
EMBED_DIM = 1536
_RERANK_SNIPPET_CHARS = 500
_JSON_ARRAY_RE = re.compile(r"\[[\s\d,]+\]")


def get_openai() -> OpenAI:
    cfg = settings()
    return OpenAI(api_key=cfg["openai_api_key"])


def embed_texts(texts: list[str], *, batch_size: int = 64) -> list[list[float]]:
    if not texts:
        return []
    client = get_openai()
    model = settings()["openai_embed_model"]
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(model=model, input=batch)
        ordered = sorted(response.data, key=lambda row: row.index)
        vectors.extend(item.embedding for item in ordered)
    return vectors


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def chat_answer(
    *,
    question: str,
    context: str,
    version: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You are Nirvana Retail Group's internal knowledge assistant. "
        "Answer only from the provided context. If the context is insufficient, say so. "
        "Cite document_id values when making factual claims. "
        "Use prior conversation turns only to interpret the latest question; "
        "do not invent facts from chat history that are not in the context. "
        f"Pipeline version: {version}."
    )
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for turn in history or []:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append(
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nContext:\n{context}",
        }
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
    )
    return (response.choices[0].message.content or "").strip()


def _parse_rank_indices(raw: str, *, n: int) -> list[int] | None:
    text = (raw or "").strip()
    if not text:
        return None
    candidates = [text]
    match = _JSON_ARRAY_RE.search(text)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, list):
            continue
        indices: list[int] = []
        seen: set[int] = set()
        for item in parsed:
            if not isinstance(item, int) or isinstance(item, bool):
                continue
            if item < 0 or item >= n or item in seen:
                continue
            seen.add(item)
            indices.append(item)
        if indices:
            return indices
    return None


def rerank_chunks(*, question: str, texts: list[str], top_k: int) -> list[int]:
    """Listwise LLM rerank: return indices of texts ordered best→worst, truncated to top_k."""
    n = len(texts)
    if n == 0 or top_k <= 0:
        return []
    if n == 1:
        return [0]

    default_order = list(range(n))
    snippets = []
    for i, text in enumerate(texts):
        body = (text or "").strip().replace("\n", " ")
        if len(body) > _RERANK_SNIPPET_CHARS:
            body = body[:_RERANK_SNIPPET_CHARS] + "…"
        snippets.append(f"[{i}] {body}")

    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You rerank retrieved document chunks for a RAG system. "
        "Rank by relevance to the question (best first). "
        "Return ONLY a JSON array of integer indices covering each chunk exactly once, "
        "e.g. [2,0,1]. No prose."
    )
    user = (
        f"Question:\n{question}\n\n"
        f"Chunks ({n} total):\n" + "\n".join(snippets)
    )
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
    except Exception:
        return default_order[:top_k]

    ranked = _parse_rank_indices(raw, n=n)
    if ranked is None:
        return default_order[:top_k]

    for idx in default_order:
        if idx not in ranked:
            ranked.append(idx)
    return ranked[:top_k]
