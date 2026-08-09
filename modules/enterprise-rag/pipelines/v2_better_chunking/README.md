# v2 — Better chunking

Section-aware H1–H3 splits + overlap → OpenAI embeddings → **Qdrant Cloud** retrieve → OpenAI generate.

Same ask path as v1; the delta is indexing only.

## Prerequisites

1. `api/.env` with `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
2. Index gold once (separate collection from v1):

```bash
# from repo root
pip install -r modules/enterprise-rag/api/requirements.txt
python modules/enterprise-rag/cli.py index --version v2_better_chunking --recreate
```

## Run

```bash
python modules/enterprise-rag/cli.py ask --version v2_better_chunking --question "When did the California laptop promotion end?"
```

## Chunk strategy

- Strip YAML frontmatter before splitting
- Split on ATX headings `#`–`###`; keep the heading as a prefix on each chunk
- Sub-chunk oversized sections at 800 chars with **120-char overlap**
- Docs without headings fall back to size + overlap on the body

## Interview notes

- Fixes v1 mid-sentence / mid-section cuts (boundary facts stay in one chunk more often).
- Tradeoff: more chunks and slightly higher index cost; retrieve/generate stack unchanged.
- Still no metadata filters — expired California promo docs can rank highly (v7 story).
- Collection name: `{QDRANT_COLLECTION_PREFIX}_v2_better_chunking` (default `nrg_gold_v2_better_chunking`).
