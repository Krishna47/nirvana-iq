# RAG version scorecard

Same gold corpus. Same curated `questions.json`. Different pipelines.

| Metric | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
|--------|----|----|----|----|----|----|----|----|----|-----|
| Citation hit rate | TBD | — | — | — | — | — | — | — | — | — |
| Answer graded score | stub | — | — | — | — | — | — | — | — | — |
| Expired-doc mistakes | TBD | — | — | — | — | — | **target: low** | — | — | — |
| p50 latency (ms) | TBD | — | — | — | — | — | — | — | — | — |
| Notes | basic stub | stub | stub | stub | stub | stub | metadata | agentic | multimodal | self-rag |

Version ids: `v1_basic_rag` … `v10_self_rag`.

## Interview demo path

1. v1 on California promo end-date → possible expired citation.
2. v7 metadata filters → exclude `status=expired`.
3. Point at this table for quality/latency tradeoffs.

## Refresh

```bash
python modules/enterprise-rag/cli.py eval --version v1_basic_rag
```
