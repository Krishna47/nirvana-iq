from __future__ import annotations

from pathlib import Path

import yaml

from src.config_loader import load_company_config, load_generation_config
from src.exporters import (
    MarkdownExporter,
    build_front_matter,
    relative_document_path,
    render_markdown_from_plan,
)
from src.models import GeneratedDocument
from src.planner import DocumentPlanner


def test_render_markdown_injects_canonical_front_matter() -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2023, 2023, seed=21)[0]
    markdown = render_markdown_from_plan(plan, "# Title\n\n## Executive Summary\nBody\n")

    assert markdown.startswith("---\n")
    front, body = markdown.split("---\n", 2)[1], markdown.split("---\n", 2)[2]
    parsed = yaml.safe_load(front)
    assert parsed["document_id"] == plan.document_id
    assert parsed["department"] == plan.department
    assert parsed["product_codes"] == plan.product_codes
    assert "Executive Summary" in body


def test_relative_path_includes_year_and_type() -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2022, 2022, seed=22)[0]
    rel = relative_document_path(plan).replace("\\", "/")
    assert rel.startswith(f"raw/{plan.year}/{plan.document_type.value}/")
    assert rel.endswith(".md")


def test_markdown_exporter_writes_file(tmp_path: Path) -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2026, 2026, seed=23)[0]
    markdown = render_markdown_from_plan(plan, "# Demo\n\nContent\n")
    document = GeneratedDocument(
        plan=plan,
        markdown=markdown,
        word_count=2,
        content_hash="abc",
        relative_path=relative_document_path(plan),
    )
    exporter = MarkdownExporter(tmp_path)
    path = exporter.write_document(document)
    assert path.exists()
    assert plan.document_id in path.read_text(encoding="utf-8")
    assert build_front_matter(plan)["owner"] == plan.owner
