# Enterprise RAG Evolution Lab (React)

Vite + React UI with separate URL routes so you can open Lab and Documents in two browser tabs.

## Prerequisites

1. API running on port 8000:
   ```bash
   uvicorn api.main:app --app-dir modules/enterprise-rag --reload --port 8000
   ```
2. Gold indexed (for Lab): `python modules/enterprise-rag/cli.py index --version v1_basic_rag`

## Run

```bash
cd modules/enterprise-rag/web
npm install
npm run dev
```

## Pages (open in separate tabs)

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:5173/lab | RAG ask / answer |
| http://127.0.0.1:5173/compare | Multi-version compare |
| http://127.0.0.1:5173/documents | Document lookup |
| http://127.0.0.1:5173/documents/NRG-POL-SALES-001 | Deep-link fetch by id |

The **Documents ↗** nav control opens `/documents` in a **new tab** so Lab stays visible.

Vite proxies `/api/*` → `http://127.0.0.1:8000`.
