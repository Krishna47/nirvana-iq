"""Load API settings from modules/enterprise-rag/api/.env."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from .paths import MODULE_ROOT

_API_ENV = MODULE_ROOT / "api" / ".env"


def load_env() -> None:
    if _API_ENV.exists():
        load_dotenv(_API_ENV, override=False)
    load_dotenv(override=False)


@lru_cache(maxsize=1)
def settings() -> dict[str, str]:
    load_env()
    required = ("OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            f"Missing env vars: {', '.join(missing)}. "
            f"Copy api/.env.example to api/.env and fill values."
        )
    return {
        "openai_api_key": os.environ["OPENAI_API_KEY"],
        "openai_embed_model": os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        "openai_chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
        "qdrant_url": os.environ["QDRANT_URL"].rstrip("/"),
        "qdrant_api_key": os.environ["QDRANT_API_KEY"],
        "qdrant_collection_prefix": os.getenv("QDRANT_COLLECTION_PREFIX", "nrg_gold"),
    }


def collection_name(version: str) -> str:
    prefix = settings()["qdrant_collection_prefix"]
    return f"{prefix}_{version}"
