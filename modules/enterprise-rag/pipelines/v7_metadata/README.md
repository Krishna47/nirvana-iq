# v7 — Metadata filters

Hybrid retrieve on the shared **v3** collection with Qdrant payload filters for
`status`, `region`, and year-on-`effective_date`.

## What failed before

Dense/hybrid/rerank/rewrite/multi-query can still surface the **expired**
California laptop promo (`NRG-POL-SALES-001` v1.0, `status=expired`, 10%) ahead
of the current approved policy (v2.0, 12%).

## What changed

- Reuse `nrg_gold_v3_hybrid_search` (no new index).
- Infer filters from the (condensed) question:
  - Default: exclude `status=expired`
  - Allow expired when the question mentions expired/retired/historical intent
  - Optional `region` match when a known region is named
  - Optional year window on `effective_date` when `2025`/`2026` appears
- Lab shows **Applied filters** for demos.

## Status

Runnable.

## Tradeoff

More product logic in the retrieve path; fewer wrong operational answers from
stale policies. Intent heuristics can miss edge cases (agentic check in v8).

## Interview talking points

1. Embeddings do not understand `status=expired` — payload filters do.
2. Same document id can have expired + approved versions; filter before generate.
3. Do not use wall-clock as-of alone when corpus dates are demo-fixed.
