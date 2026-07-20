"""Draft evaluation questions from gold trap plans and curated company traps."""

from __future__ import annotations

import json
from pathlib import Path

from .config_loader import corpus_root, ensure_data_dirs, load_company_config
from .planner import load_plans


def draft_gold_questions() -> Path:
    ensure_data_dirs("gold")
    company = load_company_config()
    traps = company["traps"]
    plans = load_plans("gold")
    by_id = {p.document_id: p for p in plans}

    promo = traps["california_promo"]
    inv = traps["inventory"]
    ret = traps["returns"]
    sales = traps["sales_report_q1"]
    risk = traps["inventory_risk"]
    cat = traps["catalog"]
    sop = traps["supplier_delay"]
    sec = traps["security"]

    curated = [
        {
            "id": "Q001",
            "question": "When did the California laptop promotion end?",
            "expected_answer": promo["current"]["expiry_date"],
            "expected_sources": [promo["document_id"]],
            "tags": ["exact", "policy"],
        },
        {
            "id": "Q002",
            "question": "What discount applied during the 2026 California laptop campaign?",
            "expected_answer": promo["current"]["discount_percent"],
            "expected_sources": [promo["document_id"]],
            "tags": ["exact", "policy"],
        },
        {
            "id": "Q003",
            "question": "What is the standard laptop reorder point?",
            "expected_answer": inv["reorder_point"],
            "expected_sources": [inv["document_id"]],
            "tags": ["exact", "policy"],
        },
        {
            "id": "Q004",
            "question": "Can an opened non-defective laptop be returned after 20 days?",
            "expected_answer": f"No. The return window is {ret['return_window_days']}.",
            "expected_sources": [ret["document_id"]],
            "tags": ["policy"],
        },
        {
            "id": "Q005",
            "question": "Why did California laptop sales decline in April 2026?",
            "expected_answer": sales["april_decline_reason"],
            "expected_sources": [
                sales["document_id"],
                risk["document_id"],
                promo["document_id"],
                inv["document_id"],
            ],
            "tags": ["multi_hop"],
        },
        {
            "id": "Q006",
            "question": "Which document version of the California laptop promotion is expired?",
            "expected_answer": promo["expired"]["version"],
            "expected_sources": [promo["document_id"]],
            "tags": ["expired_trap"],
        },
        {
            "id": "Q007",
            "question": "After how many hours should a supplier delay be escalated?",
            "expected_answer": sop["escalate_after_hours"],
            "expected_sources": [sop["document_id"]],
            "tags": ["exact", "policy"],
        },
        {
            "id": "Q008",
            "question": "Is MFA required by the information security policy?",
            "expected_answer": sec["mfa_required"],
            "expected_sources": [sec["document_id"]],
            "tags": ["exact", "policy"],
        },
        {
            "id": "Q009",
            "question": "Which SKU is called out as below reorder in the April 2026 inventory risk report?",
            "expected_answer": risk["units_below_reorder"],
            "expected_sources": [risk["document_id"]],
            "tags": ["exact", "multi_hop"],
        },
        {
            "id": "Q010",
            "question": "What is the flagship SKU in the laptop product catalog?",
            "expected_answer": cat["flagship_sku"],
            "expected_sources": [cat["document_id"]],
            "tags": ["catalog", "exact"],
        },
    ]

    # Append per-plan grounded questions (dedupe by question text)
    seen = {q["question"] for q in curated}
    idx = 11
    for plan in plans:
        if plan.document_id not in by_id:
            continue
        for eq in plan.evaluation_questions:
            if eq.question in seen:
                continue
            curated.append(
                {
                    "id": f"Q{idx:03d}",
                    "question": eq.question,
                    "expected_answer": eq.expected_answer,
                    "expected_sources": eq.expected_sources or [plan.document_id],
                    "tags": eq.tags or [],
                }
            )
            seen.add(eq.question)
            idx += 1

    filtered = [
        q for q in curated if all(src in by_id for src in q["expected_sources"])
    ]

    out = corpus_root("gold") / "evaluation" / "questions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(filtered, indent=2), encoding="utf-8")
    return out
