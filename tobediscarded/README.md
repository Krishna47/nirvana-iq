# To be discarded

Legacy / pre-migration assets parked here for later deletion.

| Path | What it was |
|------|-------------|
| `enterprise-rag/document-factory/` | Synthetic document generator |
| `nirvana-iq-enterprise-rag-corpus/` | Generated Nirvana Retail corpus + eval questions |

Active RAG work lives under `modules/enterprise-rag/`. Pipelines still read the corpus from this folder until you migrate data or delete this directory (update `modules/enterprise-rag/shared/paths.py` if you move/delete the corpus).

Do not add new work here.
