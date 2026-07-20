# RAG version ladder

Folder names use underscores for Python packages; they map to the portfolio ladder:

```text
modules/enterprise-rag/
├── pipelines/
│   ├── v1_basic_rag/       # basic RAG
│   ├── v2_better_chunking/
│   ├── v3_hybrid_search/
│   ├── v4_reranking/
│   ├── v5_query_rewrite/
│   ├── v6_multi_query/
│   ├── v7_metadata/
│   ├── v8_agentic_rag/
│   ├── v9_multimodal/
│   └── v10_self_rag/
├── evaluation/             # scorecard + eval notes
├── benchmarks/             # latency / cost / scale
├── docs/                   # this ladder
├── final-production/       # production cut of the best stack
├── document-factory/
└── data/gold/
```

## Build order

1. v1 basic RAG (embed + retrieve + generate)
2. v2 better chunking
3. v3 hybrid search
4. v4 reranking
5. v5 query rewrite
6. v6 multi-query
7. v7 metadata filters (expired-policy interview story)
8. v8 agentic RAG
9. v9 multimodal
10. v10 self-RAG
11. Promote a chosen stack into `final-production/`
