"""Intent-aware Qdrant payload filters for v7 metadata retrieval."""

from __future__ import annotations

import re
from typing import Any

from qdrant_client.http import models as qm

_EXPIRED_INTENT_RE = re.compile(
    r"(?i)\b("
    r"expired|retired|superseded|historical|previous\s+version|older\s+version|"
    r"v1\.0|version\s+1\.0"
    r")\b"
)

# Prefer full region names to avoid noisy abbreviation matches (CA/US/NY).
_REGION_ALIASES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bcalifornia\b"), "California"),
    (re.compile(r"(?i)\bunited\s+states\b|\busa\b"), "United States"),
    (re.compile(r"(?i)\btexas\b"), "Texas"),
    (re.compile(r"(?i)\bnew\s+york\b"), "New York"),
    (re.compile(r"(?i)\bflorida\b"), "Florida"),
)

_YEAR_RE = re.compile(r"\b(2025|2026)\b")


def _match_region(question: str) -> str | None:
    for pattern, region in _REGION_ALIASES:
        if pattern.search(question or ""):
            return region
    return None


def infer_metadata_filters(question: str) -> tuple[qm.Filter | None, dict[str, Any]]:
    """Build a Qdrant Filter plus a UI-friendly applied_filters dict.

    Default enterprise posture: exclude status=expired unless the question
    explicitly asks about expired/retired/historical material.
    """
    q = (question or "").strip()
    allow_expired = bool(_EXPIRED_INTENT_RE.search(q))
    region = _match_region(q)
    year_match = _YEAR_RE.search(q)
    year = year_match.group(1) if year_match else None

    must: list[qm.Condition] = []
    must_not: list[qm.Condition] = []

    if not allow_expired:
        must_not.append(
            qm.FieldCondition(key="status", match=qm.MatchValue(value="expired"))
        )

    if region:
        must.append(qm.FieldCondition(key="region", match=qm.MatchValue(value=region)))

    if year:
        # ISO date strings in payload; constrain to that calendar year (no wall-clock as-of).
        next_year = str(int(year) + 1)
        must.append(
            qm.FieldCondition(
                key="effective_date",
                range=qm.DatetimeRange(
                    gte=f"{year}-01-01T00:00:00Z",
                    lt=f"{next_year}-01-01T00:00:00Z",
                ),
            )
        )

    applied: dict[str, Any] = {
        "exclude_expired": not allow_expired,
        "region": region,
        "year": year,
    }

    if not must and not must_not:
        return None, applied

    return (
        qm.Filter(
            must=must or None,
            must_not=must_not or None,
        ),
        applied,
    )
