"""Exporter unit tests."""

from __future__ import annotations

from pathlib import Path

from src.exporters import (
    content_hash,
    jaccard_similarity,
    render_front_matter,
    word_count,
    write_csv_manifest,
)
from src.models import DocumentPlan, ManifestRecord


def test_word_count_and_hash() -> None:
    text = "Hello world. Hello again."
    assert word_count(text) == 4
    assert content_hash(text) == content_hash("  hello   world. hello again. ")


def test_jaccard_identical() -> None:
    assert jaccard_similarity("alpha beta gamma", "alpha beta gamma") == 1.0


def test_render_front_matter_contains_fields() -> None:
    plan = DocumentPlan(
        document_id="NRG-RPT-1",
        title="Report",
        document_type="report",
        department="Sales",
        region="Texas",
        version="1.0",
        status="approved",
        path="raw/2026/reports/a.md",
    )
    fm = render_front_matter(plan)
    assert "document_id: NRG-RPT-1" in fm
    assert "confidentiality: internal" in fm


def test_write_csv_manifest(tmp_path: Path) -> None:
    records = [
        ManifestRecord(
            document_id="NRG-1",
            title="T",
            document_type="policy",
            department="Sales",
            region="California",
            version="1.0",
            status="approved",
            path="raw/a.md",
            sha256="abc",
        )
    ]
    out = tmp_path / "documents.csv"
    write_csv_manifest(records, out)
    content = out.read_text(encoding="utf-8")
    assert "document_id" in content
    assert "NRG-1" in content
