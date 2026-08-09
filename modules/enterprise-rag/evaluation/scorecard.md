# RAG version scorecard

Same gold corpus. Same curated `questions.json`. Different pipelines.

| Metric | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
|--------|----|----|----|----|----|----|----|----|----|-----|
| Citation hit rate | TBD | 1.00 (n=20 smoke) | — | — | — | — | — | — | — | — |
| Answer graded score | stub | stub | — | — | — | — | — | — | — | — |
| Expired-doc mistakes | TBD | still open | — | — | — | — | **target: low** | — | — | — |
| p50 latency (ms) | TBD | ~2830 (n=20) | — | — | — | — | — | — | — | — |
| Notes | fixed 800/0 chunks | section H1-H3 + overlap 120; fixes mid-section cuts | stub | stub | stub | stub | metadata | agentic | multimodal | self-rag |

Version ids: `v1_basic_rag` … `v10_self_rag`.

## Interview demo path

1. v1 on California promo end-date → possible expired citation.
2. v7 metadata filters → exclude `status=expired`.
3. Point at this table for quality/latency tradeoffs.

## Refresh

```bash
python modules/enterprise-rag/cli.py eval --version v1_basic_rag
python modules/enterprise-rag/cli.py eval --version v2_better_chunking
```

## v1 → v2 delta

- **What failed in v1:** fixed 800-char windows with 0 overlap cut mid-sentence / mid-section; boundary facts (e.g. return windows) fragmented.
- **What changed:** strip frontmatter, split on ATX H1–H3, prefix chunks with heading, sub-chunk oversized sections with 120-char overlap.
- **Tradeoff:** more chunks / higher index cost; ask path (dense top-4 + generate) unchanged. Expired-policy ranking still open until v7.
