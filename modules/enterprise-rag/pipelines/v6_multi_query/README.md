# v6 — Multi-query fusion

LlamaIndex expands the question into multiple standalone search queries, hybrid-retrieves each against the shared **v3** collection, fuses with client-side RRF, then generates.

## Stack

1. Condense multi-turn history (if any)
2. **LlamaIndex** `expand_queries` (3 diverse phrasings)
3. Hybrid search per query (`top_k=8`) on `nrg_gold_v3_hybrid_search`
4. Client **RRF** merge → top 4
5. OpenAI generate with citations

No new index. Qdrant remains the retrieval backend.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
pip install -r modules/enterprise-rag/api/requirements.txt
```

## Demo

```bash
python modules/enterprise-rag/cli.py ask --version v6_multi_query --question "Why did California laptop sales decline in April 2026?"
```

In Evolution Lab → V6, check the **Expanded queries** panel.
