"""Pydantic models for the Nirvana IQ corpus factory."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    heading: str
    required: bool = True


class EvaluationQuestion(BaseModel):
    id: str
    question: str
    expected_answer: str
    expected_sources: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DocumentPlan(BaseModel):
    document_id: str
    title: str
    document_type: str
    department: str
    region: str
    version: str
    status: str
    effective_date: str = ""
    expiry_date: str = ""
    path: str
    required_facts: dict[str, str] = Field(default_factory=dict)
    sections: list[str] = Field(default_factory=list)
    seed: int = 0
    corpus: str = "gold"
    trap_tag: str = ""
    confidentiality: str = "internal"
    year: int | None = None
    evaluation_questions: list[EvaluationQuestion] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentPlan:
        return cls.model_validate(data)


class GeneratedDocument(BaseModel):
    plan: DocumentPlan
    markdown: str
    word_count: int = 0
    sha256: str = ""


class ManifestRecord(BaseModel):
    document_id: str
    title: str
    document_type: str
    department: str
    region: str
    version: str
    status: str
    effective_date: str = ""
    expiry_date: str = ""
    path: str
    sha256: str
    trap_tag: str = ""
    confidentiality: str = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
