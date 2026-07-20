from __future__ import annotations

from src.config_loader import load_company_config, load_generation_config
from src.exporters import render_markdown_from_plan
from src.models import DocumentType, EvaluationQuestion
from src.planner import DocumentPlanner
from src.validator import DocumentValidator, word_count


def _body_for_plan(plan, filler_words: int) -> str:
    sections = "\n\n".join(f"## {heading}\n\nPlaceholder content for {heading}." for heading in plan.required_sections)
    answers = "\n".join(
        f"{idx}. Question: {q.question}\n   Expected Answer: {q.expected_answer}"
        for idx, q in enumerate(plan.evaluation_questions, start=1)
    )
    metrics_block = (
        f"Reorder point is {plan.metrics['reorder_point_units']} sellable units. "
        f"Discount is {plan.metrics['discount_percent']}%. "
        f"SLA is {plan.metrics['sla_hours']} hours. "
        f"Fill rate target is {plan.metrics['target_fill_rate_percent']}%. "
        f"Return window is {plan.metrics['max_return_window_days']} days. "
        f"Products: {', '.join(plan.product_codes)}. "
        f"Department {plan.department} region {plan.region} status {plan.status} "
        f"confidentiality {plan.confidentiality} version {plan.version} "
        f"effective {plan.effective_date} id {plan.document_id}."
    )
    # Include expected answers and exception text verbatim.
    grounding = " ".join(q.expected_answer for q in plan.evaluation_questions)
    filler = " ".join(["operations"] * filler_words)
    return (
        f"# {plan.title}\n\n{metrics_block}\n\n{grounding}\n\n"
        f"{sections}\n\n## Evaluation Questions\n\n{answers}\n\n{filler}\n"
    )


def test_validator_accepts_well_formed_document() -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2024, 2024, seed=5)[0]
    body = _body_for_plan(plan, filler_words=plan.word_min + 50)
    markdown = render_markdown_from_plan(plan, body)

    validator = DocumentValidator(company.product_codes)
    result = validator.validate(plan, markdown)
    assert result.ok, result.errors
    assert plan.word_min <= result.word_count <= plan.word_max


def test_validator_rejects_unknown_product_codes() -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2024, 2024, seed=8)[0]
    body = _body_for_plan(plan, filler_words=plan.word_min + 40)
    body += "\nUnauthorized SKU NRG-ZZZ-9999 must never appear.\n"
    markdown = render_markdown_from_plan(plan, body)

    validator = DocumentValidator(company.product_codes)
    result = validator.validate(plan, markdown)
    assert not result.ok
    assert any("Unknown product codes" in error for error in result.errors)


def test_validator_rejects_missing_section_and_short_docs() -> None:
    company = load_company_config()
    generation = load_generation_config()
    plan = DocumentPlanner(company, generation).plan_documents(1, 2025, 2025, seed=12)[0]
    short_body = (
        f"## Executive Summary\nShort. {plan.document_id} {plan.version} "
        f"{plan.department} {plan.region} {plan.status} {plan.confidentiality} "
        f"{plan.effective_date} {plan.product_codes[0]} "
        f"{plan.metrics['reorder_point_units']} {plan.metrics['discount_percent']}% "
        f"{plan.metrics['sla_hours']} {plan.metrics['target_fill_rate_percent']} "
        f"{plan.metrics['max_return_window_days']} "
        f"{plan.evaluation_questions[0].expected_answer} "
        f"{plan.evaluation_questions[1].expected_answer} "
        f"{plan.evaluation_questions[2].expected_answer}\n"
    )
    markdown = render_markdown_from_plan(plan, short_body)
    validator = DocumentValidator(company.product_codes)
    result = validator.validate(plan, markdown)
    assert not result.ok
    assert any("Missing required section" in error for error in result.errors)
    assert any("Word count" in error for error in result.errors)
    assert word_count(markdown) < plan.word_min


def test_document_type_enum_covers_catalog() -> None:
    assert DocumentType.PRODUCT_CATALOG.value == "product_catalog"
    q = EvaluationQuestion(id="x", question="q", expected_answer="a", expected_sources=["x"])
    assert q.expected_sources == ["x"]
