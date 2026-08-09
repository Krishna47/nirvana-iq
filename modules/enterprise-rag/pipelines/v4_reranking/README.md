# v4 — Reranking

Hybrid retrieve top-N from the **v3** collection → OpenAI listwise LLM rerank → top-K → OpenAI generate.

No separate v4 index. Query-time precision boost on top of v3 recall.

## Prerequisites

1. `api/.env` with `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
2. **v3 hybrid collection already indexed:**

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
```

Do **not** run `index --version v4_reranking` — v4 shares `nrg_gold_v3_hybrid_search`.

## Run

```bash
python modules/enterprise-rag/cli.py ask --version v4_reranking --question "Can an opened non-defective laptop be returned after 20 days?"
```

## Ask path

| Step | Detail |
|------|--------|
| Retrieve | `hybrid_search("v3_hybrid_search", top_k=20)` |
| Rerank | `gpt-4.1-mini` listwise JSON index order |
| Context | Top **4** chunks |
| Generate | Same `chat_answer` as prior versions |

## Interview notes

- Fixes near-duplicate ranking (e.g. return-after-20-days → No / 15-day window, `NRG-POL-CX-004`).
- Tradeoff: one extra chat call → higher latency/cost vs v3.
- Still no metadata filters — expired California promo docs can rank highly (v7 story).
