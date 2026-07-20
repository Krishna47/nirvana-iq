# Nirvana Retail Group — Enterprise Document Factory

Production-style synthetic document generator for NirvanaIQ Enterprise RAG demos.

Python plans immutable enterprise facts; the OpenAI Responses API converts those facts into realistic internal prose. Output includes Markdown documents, manifests with SHA-256 checksums, and grounded evaluation questions.

## Setup

```bash
cd tobediscarded/enterprise-rag/document-factory
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

## Environment configuration

Set these values in `.env` (never commit secrets):

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1-mini
```

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Required for real generation |
| `OPENAI_MODEL` | Responses API model (default `gpt-4.1-mini`) |

Company facts live in `config/company.yaml`. Counts, type mix, retries, and concurrency defaults live in `config/generation.yaml`.

## Test command

```bash
python -m pytest -q
```

## Dry run

Plans documents without calling the API:

```bash
python -m src.main \
  --documents 10 \
  --start-year 2020 \
  --end-year 2026 \
  --seed 47 \
  --output output \
  --dry-run
```

Writes `output/plans.json` and `output/generation-summary.json`.

## Generate 5 documents

```bash
python -m src.main \
  --documents 5 \
  --start-year 2020 \
  --end-year 2026 \
  --seed 47 \
  --output output \
  --concurrency 3
```

## Generate 50 documents

```bash
python -m src.main \
  --documents 50 \
  --start-year 2020 \
  --end-year 2026 \
  --seed 47 \
  --output output \
  --concurrency 3
```

## Generate 1,000 documents

```bash
python -m src.main \
  --documents 1000 \
  --start-year 2020 \
  --end-year 2026 \
  --seed 47 \
  --output output \
  --concurrency 3
```

Resume after interruption:

```bash
python -m src.main --documents 1000 --seed 47 --output output --resume
```

## Expected folder structure

```text
enterprise-rag/document-factory/
├── config/
├── prompts/
├── src/
├── tests/
├── output/
│   ├── raw/<year>/<document_type>/*.md
│   ├── manifests/documents.json
│   ├── manifests/documents.csv
│   ├── evaluation/questions.json
│   ├── failures/*.json
│   ├── plans.json
│   └── generation-summary.json
├── requirements.txt
├── .env.example
├── Makefile
└── README.md
```

## Makefile shortcuts

```bash
make install
make test
make dry-run
make generate-5
make generate-50
make generate-1000
```

## Cost-control advice

- Always start with `--dry-run` to verify counts/years/seed.
- Validate prompts on `--documents 5` before scaling.
- Prefer a small/cheap model in `OPENAI_MODEL` for bulk drafts.
- Keep `--concurrency` low (default `3`) to reduce rate-limit retries.
- Use `--resume` so reruns skip completed document IDs.
- Failed generations land in `output/failures/` with plan + raw response for repair without redoing the full batch.
- Target length is enforced by validators; unexpected length failures are cheaper to inspect in small batches than in a 1,000-doc run.

## Design notes

- Deterministic planning uses `--seed`.
- Immutable fields (IDs, dates, versions, product codes, metrics, department, region, status, confidentiality) are planned in Python and validated after generation.
- Duplicate detection compares normalized text similarity against already-accepted docs in the batch.
- No LangChain dependency — OpenAI Python SDK Responses API only.
