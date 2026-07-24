# Enterprise RAG API

FastAPI surface for the React Evolution Lab. Uses **Qdrant Cloud** + OpenAI.

## Setup

```bash
cd modules/enterprise-rag/api
copy .env.example .env
# Edit .env: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

pip install -r requirements.txt
```

Do not commit `.env`. Never put secrets in `.env.example`.

## Index gold into Qdrant

```bash
# from repo root
python modules/enterprise-rag/cli.py index --version v1_basic_rag --recreate
```

Optional smoke: `--limit-docs 20`

## Run API

```bash
# from repo root
uvicorn api.main:app --app-dir modules/enterprise-rag --reload --port 8000
```

Endpoints: `GET /health`, `GET /versions`, `GET /documents/{document_id}`, `POST /ask`, `POST /compare`.

### Fetch a policy (or any doc) by id

```bash
# all versions of this id (e.g. expired + current)
curl http://127.0.0.1:8000/documents/NRG-POL-SALES-001

# only current approved policy
curl "http://127.0.0.1:8000/documents/NRG-POL-SALES-001?status=approved&document_type=policy"

# metadata only (no markdown body)
curl "http://127.0.0.1:8000/documents/NRG-POL-SALES-001?include_text=false"
```
