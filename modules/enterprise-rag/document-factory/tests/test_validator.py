"""Validator unit tests."""

from __future__ import annotations

from src.exporters import render_front_matter
from src.models import DocumentPlan, EvaluationQuestion
from src.validator import validate_document


def _sample_plan() -> DocumentPlan:
    return DocumentPlan(
        document_id="NRG-POL-TEST-001",
        title="Test Policy",
        document_type="policy",
        department="Sales",
        region="California",
        version="1.0",
        status="approved",
        effective_date="2026-01-01",
        expiry_date="",
        path="raw/2026/policies/test.md",
        required_facts={
            "document_id": "NRG-POL-TEST-001",
            "status": "approved",
            "version": "1.0",
            "product_code": "NRG-LAP-1001",
        },
        sections=["Executive Summary", "Policy Statements", "Keywords"],
        seed=1,
        corpus="gold",
        evaluation_questions=[
            EvaluationQuestion(
                id="t1",
                question="What product code is referenced?",
                expected_answer="NRG-LAP-1001",
                expected_sources=["NRG-POL-TEST-001"],
                tags=["exact"],
            )
        ],
    )


def test_validate_document_passes_when_facts_present() -> None:
    plan = _sample_plan()
    body = """
## Executive Summary
This approved policy covers NRG-LAP-1001.

## Policy Statements
Document NRG-POL-TEST-001 version 1.0 is approved for California.

## Keywords
inventory, laptop
"""
    text = render_front_matter(plan) + body
    # Pad word count into gold core range
    text = text + (" additional detail " * 80)
    errors = validate_document(
        plan,
        text,
        known_skus={"NRG-LAP-1001", "NRG-LAP-1002"},
        gen={
            "document_classes": {"core": ["policy"], "operational": []},
            "word_counts": {"core": {"min": 50, "max": 2000}},
        },
    )
    assert errors == []


def test_validate_document_flags_unknown_sku_and_missing_section() -> None:
    plan = _sample_plan()
    text = render_front_matter(plan) + """
## Executive Summary
Mentions unknown NRG-ZZZ-9999 and NRG-POL-TEST-001 version 1.0 approved.
"""
    text = text + (" word " * 100)
    errors = validate_document(
        plan,
        text,
        known_skus={"NRG-LAP-1001"},
        gen={
            "document_classes": {"core": ["policy"], "operational": []},
            "word_counts": {"core": {"min": 10, "max": 2000}},
        },
    )
    assert any("unknown product codes" in e for e in errors)
    assert any("missing section heading: Policy Statements" in e for e in errors)
