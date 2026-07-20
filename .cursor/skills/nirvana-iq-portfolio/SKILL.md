---
name: nirvana-iq-portfolio
description: >-
  Progressively builds the Nirvana IQ AI learning portfolio for interview
  showcase, especially versioned RAG improvements. Use when adding modules,
  RAG pipelines, agents, evals, or docs in nirvana-iq; when the user mentions
  AI portfolio, interview demo, RAG versions, or progressive build.
---

# Nirvana IQ Portfolio Builder

## Mission

Build interview-ready AI demos for the fictional Nirvana Retail Group.
Prefer depth over breadth: one working vertical slice before new modules.
For RAG, showcase improvements as versioned pipelines scored on the same golden set.

## Repo conventions

- Company facts: `COMPANY.md` and `modules/enterprise-rag/config/company.yaml`
- Modules: `modules/{enterprise-rag,agents,llm-apps,evals,mlops,multimodal,fine-tuning}`
- Architecture notes: `docs/architecture/`
- Corpus factory: `modules/enterprise-rag/document-factory` → `data/gold` (+ gitignored `data/scale`)
- Ignore `tobediscarded/` for all new work
- Project skills live in `.cursor/skills/` only (never `~/.cursor/skills-cursor/`)

## Build order (do not skip ahead without user request)

1. `enterprise-rag`: ingest → retrieve → cite → answer (version ladder below)
2. `evals` / `enterprise-rag/evaluation`: golden set runner + cross-version scorecard
3. `llm-apps`: thin product surface over RAG
4. `agents`: tool use + traces
5. `mlops` / `multimodal` / `fine-tuning`: one at a time

## Enterprise RAG versioning

Always improve via a new pipeline under `modules/enterprise-rag/pipelines/`.
Never overwrite an older version; keep it runnable for interview demos.

Folder layout (Python package names use underscores):

```text
pipelines/v1_basic_rag … v10_self_rag
evaluation/   benchmarks/   docs/   final-production/
```

Every version must:

- Use the shared corpus and `questions.json`
- Expose the same answer/citations interface (`shared/contracts.py`)
- Update `evaluation/scorecard.md`
- Document: what failed before, what changed, tradeoff

Preferred order:

1. `v1_basic_rag` — fixed chunks + dense retrieve + generate
2. `v2_better_chunking` — section-aware chunks + overlap
3. `v3_hybrid_search` — BM25 + dense fusion
4. `v4_reranking` — cross-encoder / LLM rerank
5. `v5_query_rewrite` — rewrite / HyDE-style reformulation
6. `v6_multi_query` — multi-query expansion + fusion
7. `v7_metadata` — status/date/region filters (expired policies)
8. `v8_agentic_rag` — retrieve → check → re-retrieve
9. `v9_multimodal` — image/table-aware retrieval
10. `v10_self_rag` — critique / self-correct before answer
11. Promote winner stack into `final-production/`

Highlight the expired California promo policy (`status: expired` vs current) as the interview story for v7 metadata.

## Framework guardrails (LangChain / LangGraph / LlamaIndex)

Do **not** add these to v1–v4 by default. Prefer measured pipeline deltas over framework adoption.

| Versions | Stack |
|----------|--------|
| v1–v4 | Plain Python + Qdrant + OpenAI + FastAPI |
| v5–v7 | Optional LlamaIndex (retrieval / indexes / metadata) |
| v8+ | LangGraph for agentic retrieve → check → retry |
| LangChain | Only as thin glue if needed; not the foundation |

Rules:

- Never rewrite an older version just to introduce a framework.
- React talks only to FastAPI; frameworks stay inside pipeline code.
- Qdrant remains the vector DB regardless of LangChain / LlamaIndex / LangGraph.
- If asked to add all three frameworks on early versions, follow this table unless the user explicitly overrides.
- UI target: React Evolution Lab (version bar + ask + sources/chunks/metrics) and Compare view (same question × versions).

Product stack (locked unless user overrides): React UI, FastAPI, Qdrant, OpenAI embeddings + chat.

## Per-module deliverables

Each module must include:

- Problem statement tied to Nirvana Retail Group
- Runnable demo (Makefile or README commands)
- Architecture note (short, with tradeoffs)
- Eval or quality signal where applicable
- "Interview talking points" section (3–5 bullets)

## Scope rules

- Minimize diff; match patterns in `modules/enterprise-rag/document-factory`
- No secrets in repo; use `.env.example` only
- Fictional data only; label as demo
- Do not start a new module until the current milestone has a runnable path
- When extending RAG, add a version — do not silently change older pipeline behavior
- Never read or copy from `tobediscarded/`

## Interview framing

When documenting, emphasize: design tradeoffs, failure modes, eval methodology,
and production-minded choices (tracing, cost, guardrails). Prefer scoreboard
deltas (v1 → vN) over feature lists.
