# Scale corpus (gitignored raw files)

Plan and generate locally — do not commit the 10k markdown files.

```bash
cd ../document-factory
python -m src.cli plan --corpus scale --n 10000 --seed 47
python -m src.cli generate --corpus scale --concurrency 10
```
