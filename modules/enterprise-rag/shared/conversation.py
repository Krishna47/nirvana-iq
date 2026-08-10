"""Multi-turn helpers: history typing, caps, retrieval condensation."""

from __future__ import annotations

import re
from typing import Any, Literal, TypedDict

from .openai_client import get_openai
from .settings import settings

ChatRole = Literal["user", "assistant"]

# Last 3 exchanges (6 messages) to bound cost/latency.
MAX_HISTORY_MESSAGES = 6

# Only call the condensing LLM when the latest turn likely needs prior context.
_NEEDS_HISTORY_RE = re.compile(
    r"(?i)\b("
    r"it|its|this|that|these|those|they|them|their|he|she|him|her|his|"
    r"the\s+(same\s+)?("
    r"policy|policies|promo|promotion|promotions|document|manual|sop|report|"
    r"sku|item|product|store|region|rule|requirement|process|procedure"
    r")"
    r")\b"
)


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


def _needs_history(question: str) -> bool:
    """True when the question likely depends on prior turns (pronouns / vague refs)."""
    return bool(_NEEDS_HISTORY_RE.search(question or ""))


def condense_for_retrieval(question: str, history: list[ChatMessage] | None) -> str:
    """Rewrite follow-up + history into a standalone search query.

    Empty history, or a self-contained latest question → return question unchanged
    (avoids LLM rewriting that can hurt dense retrieval, e.g. CEO after a promo turn).
    """
    q = (question or "").strip()
    if not q:
        return q
    prior = normalize_history(history)
    if not prior or not _needs_history(q):
        return q

    lines = [f"{m['role'].upper()}: {m['content']}" for m in prior]
    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You rewrite the latest user question into a standalone search query for a RAG system.\n"
        "Rules:\n"
        "1. Resolve pronouns/references using conversation history "
        "(it/that/this/they/those/the policy/the promotion/etc.).\n"
        "2. Keep the resolved query close to the user's wording; do not invent extra topics.\n"
        "3. Never force unrelated prior-turn entities into the query.\n"
        "4. Return ONLY the search query text — no quotes, labels, or explanation."
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
