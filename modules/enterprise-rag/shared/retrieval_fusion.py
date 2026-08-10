"""Client-side fusion helpers for multi-query retrieval."""

from __future__ import annotations

from typing import Any


def rrf_fuse(
    ranked_lists: list[list[Any]],
    *,
    k: int = 60,
    top_k: int = 4,
) -> list[Any]:
    """Reciprocal Rank Fusion across ranked hit lists keyed by point id."""
    if top_k <= 0:
        return []
    scores: dict[Any, float] = {}
    first_hit: dict[Any, Any] = {}
    for hits in ranked_lists:
        for rank, hit in enumerate(hits):
            pid = getattr(hit, "id", None)
            if pid is None:
                continue
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank + 1)
            if pid not in first_hit:
                first_hit[pid] = hit
    ordered = sorted(scores.keys(), key=lambda pid: scores[pid], reverse=True)
    return [first_hit[pid] for pid in ordered[:top_k]]
