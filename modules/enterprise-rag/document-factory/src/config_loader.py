"""Load company and generation YAML configs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

FACTORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = FACTORY_ROOT.parent
CONFIG_DIR = MODULE_ROOT / "config"
DATA_ROOT = MODULE_ROOT / "data"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_company_config(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or CONFIG_DIR / "company.yaml")


def load_generation_config(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or CONFIG_DIR / "generation.yaml")


def corpus_root(corpus: str) -> Path:
    if corpus not in {"gold", "scale"}:
        raise ValueError(f"Unknown corpus {corpus!r}; expected gold|scale")
    return DATA_ROOT / corpus


def plans_path(corpus: str) -> Path:
    return DATA_ROOT / "plans" / f"{corpus}.jsonl"


def ensure_data_dirs(corpus: str) -> None:
    root = corpus_root(corpus)
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "failures").mkdir(parents=True, exist_ok=True)
    if corpus == "gold":
        (root / "evaluation").mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "plans").mkdir(parents=True, exist_ok=True)
