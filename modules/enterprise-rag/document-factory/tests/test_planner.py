"""Planner unit tests."""

from __future__ import annotations

from src.planner import plan_gold, plan_scale


def test_plan_gold_includes_traps_and_count() -> None:
    plans = plan_gold(50, seed=47)
    assert len(plans) == 50
    statuses = {p.status for p in plans}
    assert "expired" in statuses
    assert "approved" in statuses
    promo = [p for p in plans if p.document_id == "NRG-POL-SALES-001"]
    assert len(promo) == 2
    assert all(p.evaluation_questions for p in promo)
    assert all("/202" in p.path or p.path.startswith("raw/") for p in plans)


def test_plan_gold_deterministic() -> None:
    a = plan_gold(20, seed=47)
    b = plan_gold(20, seed=47)
    assert [p.document_id for p in a] == [p.document_id for p in b]
    assert [p.path for p in a] == [p.path for p in b]


def test_plan_scale_exact_n() -> None:
    plans = plan_scale(100, seed=47)
    assert len(plans) == 100
    ids = [p.document_id for p in plans]
    assert len(ids) == len(set(ids))
