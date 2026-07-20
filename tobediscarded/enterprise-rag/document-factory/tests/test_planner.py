from __future__ import annotations

from src.config_loader import load_company_config, load_generation_config
from src.planner import DocumentPlanner, summarize_type_distribution


def test_planner_is_deterministic() -> None:
    company = load_company_config()
    generation = load_generation_config()
    planner = DocumentPlanner(company, generation)

    first = planner.plan_documents(25, 2020, 2026, seed=47)
    second = planner.plan_documents(25, 2020, 2026, seed=47)

    assert [plan.document_id for plan in first] == [plan.document_id for plan in second]
    assert [plan.model_dump(mode="json") for plan in first] == [
        plan.model_dump(mode="json") for plan in second
    ]


def test_planner_respects_count_and_year_bounds() -> None:
    company = load_company_config()
    generation = load_generation_config()
    planner = DocumentPlanner(company, generation)

    plans = planner.plan_documents(40, 2021, 2024, seed=11)
    assert len(plans) == 40
    assert all(2021 <= plan.year <= 2024 for plan in plans)
    assert len({plan.document_id for plan in plans}) == 40


def test_planner_covers_configured_types() -> None:
    company = load_company_config()
    generation = load_generation_config()
    planner = DocumentPlanner(company, generation)

    plans = planner.plan_documents(200, 2020, 2026, seed=99)
    distribution = summarize_type_distribution(plans)
    for doc_type in generation.document_type_weights:
        assert distribution.get(doc_type, 0) > 0


def test_product_codes_are_known() -> None:
    company = load_company_config()
    generation = load_generation_config()
    planner = DocumentPlanner(company, generation)
    plans = planner.plan_documents(30, 2020, 2026, seed=3)

    known = company.product_codes
    for plan in plans:
        assert plan.product_codes
        assert set(plan.product_codes).issubset(known)
        assert len(plan.evaluation_questions) == 3
