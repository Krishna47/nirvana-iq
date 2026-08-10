# v5 — Query rewrite

LlamaIndex rewrites vague/paraphrase questions into a standalone search query, then retrieves with Qdrant hybrid (dense + BM25 RRF) from the shared **v3** collection.

## Stack

1. Condense multi-turn history (shared helper, if any)
2. **LlamaIndex** `rewrite_for_retrieval` (OpenAI LLM)
3. Hybrid search on `nrg_gold_v3_hybrid_search` (top-4)
4. OpenAI generate with citations

No new index. No LlamaIndex vector store — Qdrant remains the retrieval backend.

## Setup

Requires the v3 collection:

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
pip install -r modules/enterprise-rag/api/requirements.txt
```

## Demo

```bash
python modules/enterprise-rag/cli.py ask --version v5_query_rewrite --question "How much off laptops in CA for the big Q1 promo?"
```

In Evolution Lab → V5, check the **Rewritten query** panel vs the raw user question.
