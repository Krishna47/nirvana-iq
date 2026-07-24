# Evaluation

Gold questions: [`../data/gold/evaluation/questions.json`](../data/gold/evaluation/questions.json)

## Commands

```bash
# from repo root
python modules/enterprise-rag/cli.py eval --version v1_basic_rag
```

Citation hit rate = share of questions where retrieved citations intersect `expected_sources`.

## Scorecard

Cross-version results: [scorecard.md](scorecard.md)

## Demo cases (UI paste)

Interview failure demos by version: [demo-cases/](demo-cases/)
