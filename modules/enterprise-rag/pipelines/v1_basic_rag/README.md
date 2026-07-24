# v1 — Basic RAG

Fixed-size chunks → OpenAI embeddings → **Qdrant Cloud** retrieve → OpenAI generate.

## Prerequisites

1. `api/.env` with `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
2. Index gold once:

```bash
# from repo root
pip install -r modules/enterprise-rag/api/requirements.txt
python modules/enterprise-rag/cli.py index --version v1_basic_rag --recreate
```

## Run

```bash
python modules/enterprise-rag/cli.py ask --version v1_basic_rag --question "When did the California laptop promotion end?"
```

## Interview notes

- Baseline for the scorecard; no metadata filters yet (expired docs can still rank highly).
- Collection name: `{QDRANT_COLLECTION_PREFIX}_v1_basic_rag` (default `nrg_gold_v1_basic_rag`).
