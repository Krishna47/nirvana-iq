# Nirvana IQ Document Factory

Greenfield corpus factory for Nirvana Retail Group: **plan → generate → validate → manifest**.

Does **not** use `tobediscarded/`. Writes to `../data/gold` and gitignored `../data/scale`.

## Setup

```bash
cd modules/enterprise-rag/document-factory
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Set `OPENAI_API_KEY` in `.env`. Optional: `OPENAI_GOLD_MODEL`, `OPENAI_SCALE_MODEL`, `OPENAI_MODEL`.

## Test command

```bash
python -m pytest -q
# or
make test
```

## Dry run

```bash
python -m src.cli plan --corpus gold --n 500 --seed 47
python -m src.cli generate --corpus gold --limit 10 --dry-run
```

## Generate 5 / 50 / scale

```bash
# 5 gold docs (API)
python -m src.cli generate --corpus gold --limit 5 --concurrency 3

# full gold (default 500)
python -m src.cli generate --corpus gold --concurrency 3
python -m src.cli validate --corpus gold
python -m src.cli manifest --corpus gold
python -m src.cli questions

# scale 10k (resume-safe, gitignored)
python -m src.cli plan --corpus scale --n 10000 --seed 47
python -m src.cli generate --corpus scale --concurrency 3
```

## Expected folder structure

```text
modules/enterprise-rag/
├── config/company.yaml
├── config/generation.yaml
├── document-factory/   # this package
└── data/
    ├── plans/{gold,scale}.jsonl
    ├── gold/raw/<year>/<type>/...
    ├── gold/manifests/{documents.jsonl,documents.json,documents.csv}
    ├── gold/evaluation/questions.json
    ├── gold/generation-summary.json
    └── scale/...       # gitignored raw/manifests/failures
```

## Cost-control advice

- Plan first (no API). Use `--dry-run` and `--limit` before full runs.
- Gold: stronger/cheaper mini model via `OPENAI_GOLD_MODEL`.
- Scale: cheapest capable model via `OPENAI_SCALE_MODEL`; keep concurrency at 3–5.
- Resume is on by default — re-run safely after interruptions.
- Do not commit `data/scale/` raw files.

## Enhancements

- Pydantic models for plans, questions, manifests
- Section / word-count / unknown-SKU / eval-answer validation
- Near-duplicate detection (hash + Jaccard)
- CSV + generation-summary.json exports
- Progress logging with ETA
- Per-document grounded evaluation questions on gold traps
- Year-bucketed raw paths for metadata demos
