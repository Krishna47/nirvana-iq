"""Multi-turn helpers: history typing, caps, retrieval condensation."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from .openai_client import get_openai
from .settings import settings

ChatRole = Literal["user", "assistant"]

# Last 3 exchanges (6 messages) to bound cost/latency.
MAX_HISTORY_MESSAGES = 6


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


def normalize_history(history: list[Any] | None) -> list[ChatMessage]:
    """Keep only valid user/assistant turns; cap to MAX_HISTORY_MESSAGES (tail)."""
    if not history:
        return []
    out: list[ChatMessage] = []
    for item in history:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
        else:
            role = getattr(item, "role", None)
            content = getattr(item, "content", None)
        if role not in ("user", "assistant"):
            continue
        text = (content or "").strip()
        if not text:
            continue
        out.append({"role": role, "content": text})
    if len(out) > MAX_HISTORY_MESSAGES:
        out = out[-MAX_HISTORY_MESSAGES:]
    return out


def condense_for_retrieval(question: str, history: list[ChatMessage] | None) -> str:
    """Rewrite follow-up + history into a standalone search query.

    Empty history → return question unchanged (no extra LLM call).
    """
    q = (question or "").strip()
    if not q:
        return q
    prior = normalize_history(history)
    if not prior:
        return q

    lines = [f"{m['role'].upper()}: {m['content']}" for m in prior]
    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You rewrite follow-up questions into standalone search queries for a RAG system. "
        "Use the conversation so pronouns and references are resolved. "
        "Return ONLY the search query text — no quotes, labels, or explanation."
    )
    user = (
        "Conversation so far:\n"
        + "\n".join(lines)
        + f"\n\nLatest user question:\n{q}\n\nStandalone search query:"
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
        rewritten = (response.choices[0].message.content or "").strip()
        # Drop surrounding quotes if the model adds them.
        if len(rewritten) >= 2 and rewritten[0] == rewritten[-1] and rewritten[0] in "\"'":
            rewritten = rewritten[1:-1].strip()
        return rewritten or q
    except Exception:
        return q
