"""Canonical paths to the gold Nirvana Retail corpus."""

from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]

# Active eval/demo corpus (factory output). Never point at tobediscarded.
CORPUS_ROOT = MODULE_ROOT / "data" / "gold"
MANIFEST_PATH = CORPUS_ROOT / "manifests" / "documents.json"
MANIFEST_JSONL_PATH = CORPUS_ROOT / "manifests" / "documents.jsonl"
QUESTIONS_PATH = CORPUS_ROOT / "evaluation" / "questions.json"
RAW_DOCS_ROOT = CORPUS_ROOT / "raw"
