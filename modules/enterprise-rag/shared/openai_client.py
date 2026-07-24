"""OpenAI embeddings and chat helpers (no LangChain)."""

from __future__ import annotations

from openai import OpenAI

from .settings import settings

# text-embedding-3-small
EMBED_DIM = 1536


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


def chat_answer(*, question: str, context: str, version: str) -> str:
    client = get_openai()
    model = settings()["openai_chat_model"]
    system = (
        "You are Nirvana Retail Group's internal knowledge assistant. "
        "Answer only from the provided context. If the context is insufficient, say so. "
        "Cite document_id values when making factual claims. "
        f"Pipeline version: {version}."
    )
    user = f"Question:\n{question}\n\nContext:\n{context}"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
    )
    return (response.choices[0].message.content or "").strip()
