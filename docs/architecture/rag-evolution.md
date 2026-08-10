# RAG evolution (version ladder)

Progressive retrieval improvements for Nirvana Retail Group, scored on one golden set.

## Why versioned pipelines

Interviewers should see **improvements**, not a single opaque demo. Each pipeline under
`modules/enterprise-rag/pipelines/` stays runnable so you can show v1 mistakes and later fixes.

Module-local ladder: [`modules/enterprise-rag/docs/rag-ladder.md`](../../modules/enterprise-rag/docs/rag-ladder.md)

## Ladder

| Version | Idea | Status |
|---------|------|--------|
| v1_basic_rag | Basic RAG (embed + retrieve + generate) | Runnable |
| v2_better_chunking | Section-aware chunks + overlap | Runnable |
| v3_hybrid_search | BM25 + dense fusion | Runnable |
| v4_reranking | Rerank top-N → top-K | Runnable |
| v5_query_rewrite | LlamaIndex query rewrite → hybrid retrieve | Runnable |
| v6_multi_query | LlamaIndex multi-query expand + RRF fuse | Runnable |
| v7_metadata | Status / date / region filters | Stub |
| v8_agentic_rag | Retrieve → check → re-retrieve | Stub |
| v9_multimodal | Image / table-aware retrieval | Stub |
| v10_self_rag | Critique / self-correct | Stub |
| final-production | Frozen best stack | Empty |

## Shared contract

Every version returns `PipelineResult`: answer, citations, retrieved chunks, latency.

## Corpus

Generate with `modules/enterprise-rag/document-factory` into `data/gold` (and gitignored `data/scale`).
Do not use `tobediscarded/`.

## Eval

`python modules/enterprise-rag/cli.py eval --version v1_basic_rag`

Track results in `modules/enterprise-rag/evaluation/scorecard.md`.
Benchmarks notes: `modules/enterprise-rag/benchmarks/`.

## Key interview story

Expired vs current California laptop promotion policy (`NRG-POL-SALES-001` v1.0 expired vs v2.0).
Basic retrieval can surface the expired doc; metadata filters (v7) are the enterprise fix.

## Tradeoffs to discuss

- Hybrid + rerank: higher latency/cost, better precision
- Metadata filters: more product logic, fewer wrong operational answers
- Agentic / self-RAG: multi-hop wins, harder to eval and operate

## Framework guardrails

v1–v4: plain Python + Qdrant + OpenAI + FastAPI.  
v5: LlamaIndex for query rewrite only; Qdrant hybrid retrieve unchanged.  
v6: LlamaIndex multi-query expand + client RRF; Qdrant hybrid per query.  
v5–v7: optional LlamaIndex. v8+: LangGraph for agentic loops. LangChain = thin glue only.  
See `modules/enterprise-rag/docs/rag-ladder.md` and `.cursor/rules/rag-framework-guardrails.mdc`.
