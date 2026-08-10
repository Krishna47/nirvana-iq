# Enterprise RAG

Ingest → chunk → retrieve → answer → cite over the Nirvana Retail Group corpus.

Showcase **versioned RAG improvements** (same eval set, different pipelines) for interview demos.

## Corpus factory (greenfield)

Do **not** use `tobediscarded/`. Generate data with:

[`document-factory/`](document-factory/) — plan → generate → validate → manifest

```bash
cd modules/enterprise-rag/document-factory
pip install -r requirements.txt
copy .env.example .env   # set OPENAI_API_KEY

python -m src.cli plan --corpus gold --n 50 --seed 47
python -m src.cli generate --corpus gold --concurrency 5
python -m src.cli validate --corpus gold
python -m src.cli manifest --corpus gold
python -m src.cli questions
```

Active pipeline corpus: [`data/gold/`](data/gold/). Ladder: [`docs/rag-ladder.md`](docs/rag-ladder.md). Architecture: [rag-evolution.md](../../docs/architecture/rag-evolution.md)

## Version ladder

| Version | Focus | Status |
|---------|--------|--------|
| [v1_basic_rag](pipelines/v1_basic_rag/) | Basic RAG | Runnable |
| [v2_better_chunking](pipelines/v2_better_chunking/) | Section-aware chunks | Runnable |
| [v3_hybrid_search](pipelines/v3_hybrid_search/) | BM25 + dense | Runnable |
| [v4_reranking](pipelines/v4_reranking/) | Rerank top-k | Runnable |
| [v5_query_rewrite](pipelines/v5_query_rewrite/) | LlamaIndex rewrite + hybrid | Runnable |
| [v6_multi_query](pipelines/v6_multi_query/) | Multi-query fusion | Stub |
| [v7_metadata](pipelines/v7_metadata/) | Status / date / region filters | Stub |
| [v8_agentic_rag](pipelines/v8_agentic_rag/) | Retrieve → check → re-retrieve | Stub |
| [v9_multimodal](pipelines/v9_multimodal/) | Image / table-aware | Stub |
| [v10_self_rag](pipelines/v10_self_rag/) | Critique / self-correct | Stub |

Winner stack → [`final-production/`](final-production/).

## Quick start

```bash
# from repo root
pip install -r modules/enterprise-rag/api/requirements.txt
# ensure modules/enterprise-rag/api/.env has OpenAI + Qdrant Cloud keys

python modules/enterprise-rag/cli.py index --version v1_basic_rag --recreate
python modules/enterprise-rag/cli.py list
python modules/enterprise-rag/cli.py ask --version v1_basic_rag --question "When did the California laptop promotion end?"
python modules/enterprise-rag/cli.py eval --version v1_basic_rag --limit 20

uvicorn api.main:app --app-dir modules/enterprise-rag --reload --port 8000
```

UI (separate terminal):

```bash
cd modules/enterprise-rag/web
npm install
npm run dev
```

Open http://127.0.0.1:5173 (proxies `/api` → FastAPI).

### Multi-turn Lab chat

Evolution Lab supports **true multi-turn** on runnable versions (v1–v4):

1. Prior turns are sent with each `POST /ask` as `messages`.
2. The backend **condenses** history + the latest question into a standalone `search_query` for retrieval.
3. Generation uses conversation history + retrieved chunks.
4. Metrics tab shows `search_query` vs the raw user question (useful for demos).
5. Compare and CLI eval stay single-turn. Each Lab version keeps its own chat thread.

Showcase script: [`evaluation/demo-cases/multi_turn_chat.md`](evaluation/demo-cases/multi_turn_chat.md).

## Layout

```text
modules/enterprise-rag/
├── config/
├── document-factory/
├── data/gold/
├── pipelines/          # v1_basic_rag … v10_self_rag
├── evaluation/         # scorecard
├── benchmarks/
├── docs/
├── final-production/
├── cli.py
└── shared/
```

## Interview talking points

- Same gold `questions.json` for every pipeline version
- Expired policy traps are intentional (v7 metadata story)
- Scale corpus proves indexing/latency; gold proves quality
- Prefer adding `vN` over mutating older pipelines

## Next steps

1. Fill [evaluation/scorecard.md](evaluation/scorecard.md) for v1–v5 after full evals
2. Climb the ladder: v6 multi-query against remaining gold failures
