# Gold corpus

Generate with the document factory:

```bash
cd ../document-factory
python -m src.cli plan --corpus gold --n 500 --seed 47
python -m src.cli generate --corpus gold
python -m src.cli validate --corpus gold
python -m src.cli manifest --corpus gold
python -m src.cli questions
```
