"""OpenAI Responses API client with retries and exponential backoff."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

logger = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    """Raised when the model call fails after retries."""


class LLMClient:
    """Thin wrapper around the OpenAI Responses API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int = 4,
        base_delay_seconds: float = 1.5,
        client: OpenAI | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        if client is not None:
            self._client = client
        elif self.api_key:
            self._client = OpenAI(api_key=self.api_key)
        else:
            self._client = None

    def require_ready(self) -> None:
        if not self.api_key or self._client is None:
            raise LLMClientError(
                "OPENAI_API_KEY is not set. Configure it in the environment or .env file."
            )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.require_ready()
        assert self._client is not None

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.responses.create(
                    model=self.model,
                    input=[
                        {
                            "role": "system",
                            "content": [{"type": "input_text", "text": system_prompt}],
                        },
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": user_prompt}],
                        },
                    ],
                )
                text = self._extract_text(response)
                if not text.strip():
                    raise LLMClientError("Empty response from model")
                return text
            except (RateLimitError, APIConnectionError, APIStatusError, LLMClientError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                delay = self.base_delay_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "LLM attempt %s/%s failed (%s). Retrying in %.1fs",
                    attempt,
                    self.max_retries,
                    exc,
                    delay,
                )
                time.sleep(delay)

        raise LLMClientError(f"Model generation failed after {self.max_retries} attempts: {last_error}")

    @staticmethod
    def _extract_text(response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text

        chunks: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks).strip()
