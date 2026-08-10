# RAG version scorecard

Same gold corpus. Same curated `questions.json`. Different pipelines.

| Metric | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
|--------|----|----|----|----|----|----|----|----|----|-----|
| Citation hit rate | TBD | 1.00 (n=20 smoke) | 1.00 (n=20 smoke) | 1.00 (n=20 smoke) | 1.00 (n=20 smoke) | 1.00 (n=20 smoke) | 1.00 (n=20 smoke) | — | — | — |
| Answer graded score | stub | stub | stub | stub | stub | stub | stub | — | — | — |
| Expired-doc mistakes | TBD | still open | still open | still open | still open | still open | low (exclude expired by default) | — | — | — |
| p50 latency (ms) | TBD | ~2830 (n=20) | ~2607 (n=20) | ~4180 (n=20) | ~3584 (n=20) | ~6360 (n=20) | ~3631 (n=20) | — | — | — |
| Notes | fixed 800/0 chunks | section H1-H3 + overlap 120; fixes mid-section cuts | dense + BM25 RRF; SKU/ID exact match | hybrid N=20 + LLM rerank to K=4 | LlamaIndex rewrite → hybrid top-4 on v3 | LlamaIndex multi-query + client RRF on v3 | hybrid on v3 + payload filters | agentic | multimodal | self-rag |

Version ids: `v1_basic_rag` … `v10_self_rag`.

## Interview demo path

1. v1 on California promo end-date → possible expired citation.
2. v7 metadata filters → exclude `status=expired`.
3. Point at this table for quality/latency tradeoffs.

## Refresh

```bash
python modules/enterprise-rag/cli.py eval --version v1_basic_rag
python modules/enterprise-rag/cli.py eval --version v2_better_chunking
python modules/enterprise-rag/cli.py eval --version v3_hybrid_search
python modules/enterprise-rag/cli.py eval --version v4_reranking
python modules/enterprise-rag/cli.py eval --version v5_query_rewrite
python modules/enterprise-rag/cli.py eval --version v6_multi_query
python modules/enterprise-rag/cli.py eval --version v7_metadata
```

## v1 → v2 delta

- **What failed in v1:** fixed 800-char windows with 0 overlap cut mid-sentence / mid-section; boundary facts (e.g. return windows) fragmented.
- **What changed:** strip frontmatter, split on ATX H1–H3, prefix chunks with heading, sub-chunk oversized sections with 120-char overlap.
- **Tradeoff:** more chunks / higher index cost; ask path (dense top-4 + generate) unchanged. Expired-policy ranking still open until v7.

## v2 → v3 delta

- **What failed in v2:** dense-only retrieval misses or buries literal SKUs/IDs (`NRG-LAP-1001`, `NRG-LAP-1002`).
- **What changed:** Qdrant collection with named `dense` + sparse `bm25` (IDF); prefetch both and fuse with RRF; keep v2 section chunking.
- **Tradeoff:** FastEmbed BM25 at index/query time and dual vectors; expired-policy ranking still open until v7.

## v3 → v4 delta

- **What failed in v3:** hybrid recall can still put near-duplicate / wrong-policy chunks above the best answer (e.g. return-after-20-days ranking).
- **What changed:** retrieve hybrid N=20 from the shared v3 collection, OpenAI listwise LLM rerank to K=4, then generate. No new index.
- **Tradeoff:** extra chat call (latency/cost); expired-policy ranking still open until v7.

## v4 → v5 delta

- **What failed in v4:** rerank only reorders candidates already retrieved; vague/paraphrase questions may never surface the right doc in top-N.
- **What changed:** LlamaIndex rewrites the query into a standalone search string, then hybrid top-4 on the shared v3 collection. No new index; no v4 rerank in this version.
- **Tradeoff:** extra LLM rewrite call (latency/cost); expired-policy ranking still open until v7; multi-query coverage left to v6.

## v5 → v6 delta

- **What failed in v5:** a single rewrite can miss alternate angles (e.g. promo expiry vs inventory for “why did sales decline?”).
- **What changed:** LlamaIndex expands to 3 search queries, hybrid retrieve each on the shared v3 collection, client-side RRF fuse to top-4, then generate. No new index; no v4 rerank.
- **Tradeoff:** N hybrid searches + expand LLM call (higher latency/cost); expired-policy ranking still open until v7.

## v6 → v7 delta

- **What failed in v6:** multi-query still ranks `status=expired` California promo chunks alongside approved ones; embeddings ignore lifecycle metadata.
- **What changed:** hybrid top-4 on the shared v3 collection with Qdrant payload filters — default exclude `status=expired`, optional region/year; allow expired when the question has expired/retired intent. No new index; no rewrite/multi-query stack.
- **Tradeoff:** more retrieve-path product logic; fewer wrong operational answers from stale policies. Intent heuristics can miss edge cases (v8).
