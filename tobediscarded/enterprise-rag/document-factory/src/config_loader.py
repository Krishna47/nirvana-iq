"""Load YAML configuration and prompt templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


FACTORY_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = FACTORY_ROOT / "config"
PROMPTS_DIR = FACTORY_ROOT / "prompts"


class ProductConfig(BaseModel):
    code: str
    name: str
    category: str
    supplier: str


class HeadquartersConfig(BaseModel):
    city: str
    state: str
    country: str


class CompanyConfig(BaseModel):
    company_name: str
    headquarters: HeadquartersConfig
    regions: list[str]
    departments: list[str]
    products: list[ProductConfig]
    suppliers: list[str]
    systems: list[str]
    confidentiality_levels: list[str]
    statuses: list[str]
    owners_by_department: dict[str, str]

    @property
    def product_codes(self) -> set[str]:
        return {product.code for product in self.products}

    def product_by_code(self, code: str) -> ProductConfig:
        for product in self.products:
            if product.code == code:
                return product
        raise KeyError(code)


class GenerationConfig(BaseModel):
    default_documents: int = 1000
    default_start_year: int = 2020
    default_end_year: int = 2026
    default_seed: int = 47
    default_concurrency: int = 3
    max_retries: int = 4
    retry_base_delay_seconds: float = 1.5
    duplicate_similarity_threshold: float = 0.92
    document_type_weights: dict[str, int]
    word_counts: dict[str, dict[str, int]]
    document_classes: dict[str, list[str]]
    type_prefixes: dict[str, str]
    required_sections: dict[str, Any] = Field(default_factory=dict)


PROMPT_FILES: dict[str, str] = {
    "policy": "policy_prompt.txt",
    "procedure": "procedure_prompt.txt",
    "report": "report_prompt.txt",
    "runbook": "runbook_prompt.txt",
    "incident_report": "incident_prompt.txt",
    "meeting_minutes": "meeting_prompt.txt",
    "contract": "contract_prompt.txt",
    "product_catalog": "product_catalog_prompt.txt",
    "architecture_document": "architecture_prompt.txt",
    "announcement": "announcement_prompt.txt",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_company_config(path: Path | None = None) -> CompanyConfig:
    config_path = path or (CONFIG_DIR / "company.yaml")
    return CompanyConfig.model_validate(load_yaml(config_path))


def load_generation_config(path: Path | None = None) -> GenerationConfig:
    config_path = path or (CONFIG_DIR / "generation.yaml")
    return GenerationConfig.model_validate(load_yaml(config_path))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_system_prompt() -> str:
    return load_text(PROMPTS_DIR / "system_prompt.txt")


def load_type_prompt(document_type: str, word_min: int, word_max: int) -> str:
    filename = PROMPT_FILES.get(document_type)
    if not filename:
        raise KeyError(f"No prompt mapped for document type: {document_type}")
    template = load_text(PROMPTS_DIR / filename)
    return template.replace("{{word_min}}", str(word_min)).replace("{{word_max}}", str(word_max))
