"""Pydantic models for planning, generation, evaluation, and manifests."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    POLICY = "policy"
    PROCEDURE = "procedure"
    REPORT = "report"
    RUNBOOK = "runbook"
    INCIDENT_REPORT = "incident_report"
    MEETING_MINUTES = "meeting_minutes"
    CONTRACT = "contract"
    PRODUCT_CATALOG = "product_catalog"
    ARCHITECTURE_DOCUMENT = "architecture_document"
    ANNOUNCEMENT = "announcement"


class DocumentSection(BaseModel):
    heading: str
    content: str = ""


class EvaluationQuestion(BaseModel):
    id: str
    question: str
    expected_answer: str
    expected_sources: list[str] = Field(default_factory=list)


class DocumentPlan(BaseModel):
    document_id: str
    title: str
    document_type: DocumentType
    year: int
    department: str
    region: str
    version: str
    status: str
    confidentiality: str
    owner: str
    effective_date: str
    expiry_date: str | None = None
    published_date: str
    product_codes: list[str] = Field(default_factory=list)
    suppliers: list[str] = Field(default_factory=list)
    systems: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    facts: dict[str, Any] = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    evaluation_questions: list[EvaluationQuestion] = Field(default_factory=list)
    required_sections: list[str] = Field(default_factory=list)
    word_min: int
    word_max: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        if value < 2020 or value > 2026:
            raise ValueError("year must be between 2020 and 2026 inclusive")
        return value


class GeneratedDocument(BaseModel):
    plan: DocumentPlan
    markdown: str
    sections: list[DocumentSection] = Field(default_factory=list)
    word_count: int = 0
    content_hash: str = ""
    relative_path: str = ""


class ManifestEntry(BaseModel):
    document_id: str
    title: str
    department: str
    document_type: str
    region: str
    version: str
    status: str
    effective_date: str
    expiry_date: str | None = None
    confidentiality: str
    owner: str
    year: int
    path: str
    sha256: str
    word_count: int
    product_codes: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class GenerationSummary(BaseModel):
    seed: int
    documents_requested: int
    generated: int
    skipped: int
    failed: int
    start_year: int
    end_year: int
    output_dir: str
    dry_run: bool
    elapsed_seconds: float
    estimated_completion: str | None = None
