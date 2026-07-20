# Nirvana IQ

Portfolio lab: end-to-end AI systems for the fictional **Nirvana Retail Group** — retrieval, agents, evals, and ops.

## Layout

```text
├── COMPANY.md              # fictional company universe
├── modules/                # AI engineering tracks
│   ├── enterprise-rag/
│   ├── agents/
│   ├── llm-apps/
│   ├── evals/
│   ├── mlops/
│   ├── multimodal/
│   └── fine-tuning/
├── shared/                 # company facts, schemas, shared assets
└── docs/architecture/      # diagrams and design notes
```

## Start here

1. Read [COMPANY.md](COMPANY.md)
2. Explore [modules/](modules/)
3. Generate gold corpus: `modules/enterprise-rag/document-factory` (see its README)

## Status

Folder skeleton only for most tracks. Enterprise RAG uses a greenfield LLM factory under `modules/enterprise-rag/document-factory/` writing to `data/gold` (and gitignored `data/scale`). Do not use `tobediscarded/` for new work.

RAG version ladder (`v1_basic_rag` … `v10_self_rag` + evaluation/benchmarks/final-production) lives under `modules/enterprise-rag/`. Project agent skill: `.cursor/skills/nirvana-iq-portfolio/`.
