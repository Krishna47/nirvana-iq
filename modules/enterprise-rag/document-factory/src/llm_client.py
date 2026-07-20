"""OpenAI client for document generation."""

from __future__ import annotations

import os
import time
from pathlib import Path

from openai import OpenAI


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class LLMClient:
    def __init__(self, model: str, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.model = model
        self.client = OpenAI(api_key=key)

    def complete(self, system: str, user: str, max_retries: int = 3, base_delay: float = 1.5) -> str:
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                text = getattr(response, "output_text", None)
                if text:
                    return text.strip()
                # Fallback: concatenate output content
                chunks: list[str] = []
                for item in getattr(response, "output", []) or []:
                    for content in getattr(item, "content", []) or []:
                        if getattr(content, "type", "") == "output_text":
                            chunks.append(content.text)
                if chunks:
                    return "\n".join(chunks).strip()
                raise RuntimeError("Empty model response")
            except Exception as exc:  # noqa: BLE001 — retry then raise
                last_error = exc
                time.sleep(base_delay * (2**attempt))
        raise RuntimeError(f"LLM call failed after retries: {last_error}")
