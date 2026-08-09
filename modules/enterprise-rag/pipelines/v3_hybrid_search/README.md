# v3 — Hybrid search

Section chunks (from v2) → OpenAI dense + FastEmbed BM25 sparse → **Qdrant RRF** → OpenAI generate.

Same generate path as v1/v2; the delta is dual-channel retrieval for exact tokens (SKUs, IDs).

## Prerequisites

1. `api/.env` with `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
2. `pip install -r modules/enterprise-rag/api/requirements.txt` (needs `qdrant-client[fastembed]`)
3. Index gold once:

```bash
# from repo root
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
```

## Run

```bash
python modules/enterprise-rag/cli.py ask --version v3_hybrid_search --question "Which SKU is called out as below reorder in the April 2026 inventory risk report?"
python modules/enterprise-rag/cli.py ask --version v3_hybrid_search --question "What is the flagship SKU in the laptop product catalog?"
```

## Collection schema

- Named dense vector `dense` (OpenAI `text-embedding-3-small`, 1536, cosine)
- Named sparse vector `bm25` (`Qdrant/bm25`, IDF modifier)
- Query: prefetch 20 dense + 20 BM25 → `FusionQuery(RRF)` → top 4
- Collection: `{QDRANT_COLLECTION_PREFIX}_v3_hybrid_search` (default `nrg_gold_v3_hybrid_search`)

## Interview notes

- Fixes dense-only SKU/ID misses (e.g. `NRG-LAP-1001`, `NRG-LAP-1002`).
- Tradeoff: dual vectors and FastEmbed at index/query time; slightly higher cost/latency vs dense-only.
- Still no metadata filters — expired California promo docs can rank highly (v7 story).
- Chunking inherits v2 section-aware splits (not a regression to fixed 800/0).
