"""Seeded planners for gold (traps + fillers) and scale (cartesian) corpora."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Iterable

from .config_loader import (
    ensure_data_dirs,
    load_company_config,
    load_generation_config,
    plans_path,
)
from .models import DocumentPlan, EvaluationQuestion


def _folder(gen: dict[str, Any], doc_type: str) -> str:
    folders = gen.get("document_type_folders") or {}
    return folders.get(doc_type, "misc")


def _year_from_date(date_str: str, default: int = 2026) -> int:
    if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
        return int(date_str[:4])
    return default


def _raw_path(gen: dict[str, Any], doc_type: str, year: int, filename: str) -> str:
    return f"raw/{year}/{_folder(gen, doc_type)}/{filename}"


def _merge_sections(gen: dict[str, Any], doc_type: str, specific: list[str]) -> list[str]:
    req = gen.get("required_sections") or {}
    common = list(req.get("common") or [])
    by_type = list((req.get("by_type") or {}).get(doc_type) or [])
    seen: set[str] = set()
    out: list[str] = []
    for heading in specific + by_type + common:
        if heading not in seen:
            seen.add(heading)
            out.append(heading)
    return out


def _write_jsonl(path: Path, plans: Iterable[DocumentPlan]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for plan in plans:
            handle.write(json.dumps(plan.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    return count


def _gold_trap_plans(company: dict[str, Any], gen: dict[str, Any], seed: int) -> list[DocumentPlan]:
    traps = company["traps"]
    plans: list[DocumentPlan] = []

    promo = traps["california_promo"]
    for label, block in (("current", promo["current"]), ("expired", promo["expired"])):
        version = block["version"]
        status = block["status"]
        suffix = "v2" if label == "current" else "v1-expired"
        year = _year_from_date(block["effective_date"])
        path = _raw_path(
            gen, "policy", year, f"01-california-laptop-promotion-policy-{suffix}.md"
        )
        facts = {
            "document_id": promo["document_id"],
            "version": version,
            "status": status,
            "effective_date": block["effective_date"],
            "expiry_date": block["expiry_date"],
            "discount_percent": block["discount_percent"],
            "category": block["category"],
            "region": promo["region"],
        }
        eval_qs = (
            [
                EvaluationQuestion(
                    id="promo-end",
                    question="When did the California laptop promotion end?",
                    expected_answer=block["expiry_date"],
                    expected_sources=[promo["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="promo-discount",
                    question="What discount applied during this California laptop campaign?",
                    expected_answer=block["discount_percent"],
                    expected_sources=[promo["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="promo-status",
                    question="What is the status of this California laptop promotion policy version?",
                    expected_answer=status,
                    expected_sources=[promo["document_id"]],
                    tags=["expired_trap" if label == "expired" else "policy"],
                ),
            ]
            if label == "current"
            else [
                EvaluationQuestion(
                    id="promo-expired-version",
                    question="Which document version of the California laptop promotion is expired?",
                    expected_answer=version,
                    expected_sources=[promo["document_id"]],
                    tags=["expired_trap"],
                ),
                EvaluationQuestion(
                    id="promo-expired-discount",
                    question="What discount applied in the expired California laptop campaign?",
                    expected_answer=block["discount_percent"],
                    expected_sources=[promo["document_id"]],
                    tags=["expired_trap"],
                ),
                EvaluationQuestion(
                    id="promo-expired-status",
                    question="What status marks the retired California laptop promotion policy?",
                    expected_answer=status,
                    expected_sources=[promo["document_id"]],
                    tags=["expired_trap"],
                ),
            ]
        )
        plans.append(
            DocumentPlan(
                document_id=promo["document_id"],
                title=promo["title"],
                document_type="policy",
                department=promo["department"],
                region=promo["region"],
                version=version,
                status=status,
                effective_date=block["effective_date"],
                expiry_date=block["expiry_date"],
                path=path,
                required_facts=facts,
                sections=_merge_sections(
                    gen,
                    "policy",
                    ["Purpose", "Eligibility", "Promotion Period", "Discount", "Exceptions"],
                ),
                seed=seed,
                corpus="gold",
                trap_tag="expired_trap" if label == "expired" else "policy",
                year=year,
                evaluation_questions=eval_qs,
            )
        )

    inv = traps["inventory"]
    year = _year_from_date(inv["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=inv["document_id"],
            title=inv["title"],
            document_type="policy",
            department=inv["department"],
            region=inv["region"],
            version=inv["version"],
            status=inv["status"],
            effective_date=inv["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "policy", year, "03-inventory-replenishment-policy.md"),
            required_facts={
                "document_id": inv["document_id"],
                "reorder_point": inv["reorder_point"],
                "laptop_sku_example": inv["laptop_sku_example"],
                "version": inv["version"],
                "status": inv["status"],
            },
            sections=_merge_sections(
                gen, "policy", ["Purpose", "Reorder Rules", "Escalation", "Metrics"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="policy",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="inv-reorder",
                    question="What is the standard laptop reorder point?",
                    expected_answer=inv["reorder_point"],
                    expected_sources=[inv["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="inv-sku",
                    question="Which laptop SKU is cited in the inventory replenishment policy?",
                    expected_answer=inv["laptop_sku_example"],
                    expected_sources=[inv["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="inv-version",
                    question="What version is the inventory replenishment policy?",
                    expected_answer=inv["version"],
                    expected_sources=[inv["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    ret = traps["returns"]
    year = _year_from_date(ret["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=ret["document_id"],
            title=ret["title"],
            document_type="policy",
            department=ret["department"],
            region=ret["region"],
            version=ret["version"],
            status=ret["status"],
            effective_date=ret["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "policy", year, "04-electronics-return-policy.md"),
            required_facts={
                "document_id": ret["document_id"],
                "return_window_days": ret["return_window_days"],
                "version": ret["version"],
                "status": ret["status"],
            },
            sections=_merge_sections(
                gen, "policy", ["Purpose", "Return Window", "Exclusions", "Refunds"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="policy",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="ret-window",
                    question="What is the electronics return window?",
                    expected_answer=ret["return_window_days"],
                    expected_sources=[ret["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="ret-20days",
                    question="Can an opened non-defective laptop be returned after 20 days?",
                    expected_answer=ret["return_window_days"],
                    expected_sources=[ret["document_id"]],
                    tags=["policy"],
                ),
                EvaluationQuestion(
                    id="ret-status",
                    question="What is the status of the electronics return policy?",
                    expected_answer=ret["status"],
                    expected_sources=[ret["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    sec = traps["security"]
    year = _year_from_date(sec["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=sec["document_id"],
            title=sec["title"],
            document_type="policy",
            department=sec["department"],
            region=sec["region"],
            version=sec["version"],
            status=sec["status"],
            effective_date=sec["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "policy", year, "09-information-security-policy.md"),
            required_facts={
                "document_id": sec["document_id"],
                "mfa_required": sec["mfa_required"],
                "version": sec["version"],
                "status": sec["status"],
            },
            sections=_merge_sections(
                gen, "policy", ["Purpose", "Access Control", "MFA", "Incident Reporting"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="policy",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="sec-mfa",
                    question="Is MFA required by the information security policy?",
                    expected_answer=sec["mfa_required"],
                    expected_sources=[sec["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="sec-version",
                    question="What version is the information security policy?",
                    expected_answer=sec["version"],
                    expected_sources=[sec["document_id"]],
                    tags=["policy"],
                ),
                EvaluationQuestion(
                    id="sec-status",
                    question="What is the status of the information security policy?",
                    expected_answer=sec["status"],
                    expected_sources=[sec["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    sop = traps["supplier_delay"]
    year = _year_from_date(sop["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=sop["document_id"],
            title=sop["title"],
            document_type="procedure",
            department=sop["department"],
            region=sop["region"],
            version=sop["version"],
            status=sop["status"],
            effective_date=sop["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "procedure", year, "06-supplier-delay-sop.md"),
            required_facts={
                "document_id": sop["document_id"],
                "escalate_after_hours": sop["escalate_after_hours"],
                "version": sop["version"],
                "status": sop["status"],
            },
            sections=_merge_sections(
                gen, "procedure", ["Purpose", "Triggers", "Steps", "Escalation"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="policy",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="sop-escalate",
                    question="After how many hours should a supplier delay be escalated?",
                    expected_answer=sop["escalate_after_hours"],
                    expected_sources=[sop["document_id"]],
                    tags=["exact", "policy"],
                ),
                EvaluationQuestion(
                    id="sop-version",
                    question="What version is the supplier delay SOP?",
                    expected_answer=sop["version"],
                    expected_sources=[sop["document_id"]],
                    tags=["policy"],
                ),
                EvaluationQuestion(
                    id="sop-status",
                    question="What is the status of the supplier delay SOP?",
                    expected_answer=sop["status"],
                    expected_sources=[sop["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    sales = traps["sales_report_q1"]
    year = _year_from_date(sales["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=sales["document_id"],
            title=sales["title"],
            document_type="report",
            department=sales["department"],
            region=sales["region"],
            version=sales["version"],
            status=sales["status"],
            effective_date=sales["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "report", year, "10-q1-2026-sales-report.md"),
            required_facts={
                "document_id": sales["document_id"],
                "april_decline_reason": sales["april_decline_reason"],
                "region": sales["region"],
                "status": sales["status"],
            },
            sections=_merge_sections(
                gen, "report", ["Summary", "Metrics", "April Decline", "Recommendations"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="multi_hop",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="sales-decline",
                    question="Why did California laptop sales decline in April 2026?",
                    expected_answer=sales["april_decline_reason"],
                    expected_sources=[sales["document_id"]],
                    tags=["multi_hop"],
                ),
                EvaluationQuestion(
                    id="sales-region",
                    question="Which region does the Q1 2026 laptop sales report cover?",
                    expected_answer=sales["region"],
                    expected_sources=[sales["document_id"]],
                    tags=["exact"],
                ),
                EvaluationQuestion(
                    id="sales-status",
                    question="What is the status of the Q1 2026 sales report?",
                    expected_answer=sales["status"],
                    expected_sources=[sales["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    risk = traps["inventory_risk"]
    year = _year_from_date(risk["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=risk["document_id"],
            title=risk["title"],
            document_type="report",
            department=risk["department"],
            region=risk["region"],
            version=risk["version"],
            status=risk["status"],
            effective_date=risk["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "report", year, "11-inventory-risk-report.md"),
            required_facts={
                "document_id": risk["document_id"],
                "units_below_reorder": risk["units_below_reorder"],
                "region": risk["region"],
                "status": risk["status"],
            },
            sections=_merge_sections(
                gen, "report", ["Summary", "Risk SKUs", "Root Causes", "Actions"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="multi_hop",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="risk-sku",
                    question="Which SKU is below reorder in the April 2026 inventory risk report?",
                    expected_answer=risk["units_below_reorder"],
                    expected_sources=[risk["document_id"]],
                    tags=["exact", "multi_hop"],
                ),
                EvaluationQuestion(
                    id="risk-region",
                    question="Which region does the inventory risk report cover?",
                    expected_answer=risk["region"],
                    expected_sources=[risk["document_id"]],
                    tags=["exact"],
                ),
                EvaluationQuestion(
                    id="risk-status",
                    question="What is the status of the inventory risk report?",
                    expected_answer=risk["status"],
                    expected_sources=[risk["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    cat = traps["catalog"]
    products = company.get("products") or []
    sku_facts = {p["code"]: p["name"] for p in products[:4]}
    required = {
        "document_id": cat["document_id"],
        "flagship_sku": cat["flagship_sku"],
        "status": cat["status"],
        "version": cat["version"],
        **{f"sku_{i}": code for i, code in enumerate(sku_facts.keys(), start=1)},
    }
    year = _year_from_date(cat["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=cat["document_id"],
            title=cat["title"],
            document_type="catalog",
            department=cat["department"],
            region=cat["region"],
            version=cat["version"],
            status=cat["status"],
            effective_date=cat["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "catalog", year, "12-laptop-product-catalog.md"),
            required_facts=required,
            sections=_merge_sections(
                gen, "catalog", ["Overview", "Products", "Pricing Notes", "Availability"]
            ),
            seed=seed,
            corpus="gold",
            trap_tag="catalog",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="cat-flagship",
                    question="What is the flagship SKU in the laptop product catalog?",
                    expected_answer=cat["flagship_sku"],
                    expected_sources=[cat["document_id"]],
                    tags=["catalog", "exact"],
                ),
                EvaluationQuestion(
                    id="cat-version",
                    question="What version is the laptop product catalog?",
                    expected_answer=cat["version"],
                    expected_sources=[cat["document_id"]],
                    tags=["catalog"],
                ),
                EvaluationQuestion(
                    id="cat-status",
                    question="What is the status of the laptop product catalog?",
                    expected_answer=cat["status"],
                    expected_sources=[cat["document_id"]],
                    tags=["catalog"],
                ),
            ],
        )
    )

    exec_dir = traps["executive_leadership"]
    year = _year_from_date(exec_dir["effective_date"])
    plans.append(
        DocumentPlan(
            document_id=exec_dir["document_id"],
            title=exec_dir["title"],
            document_type="manual",
            department=exec_dir["department"],
            region=exec_dir["region"],
            version=exec_dir["version"],
            status=exec_dir["status"],
            effective_date=exec_dir["effective_date"],
            expiry_date="",
            path=_raw_path(gen, "manual", year, "13-executive-leadership-directory.md"),
            required_facts={
                "document_id": exec_dir["document_id"],
                "ceo_name": exec_dir["ceo_name"],
                "ceo_title": exec_dir["ceo_title"],
                "version": exec_dir["version"],
                "status": exec_dir["status"],
            },
            sections=_merge_sections(
                gen,
                "manual",
                ["Purpose", "Chief Executive Officer", "Headquarters", "Exceptions"],
            ),
            seed=seed,
            corpus="gold",
            trap_tag="leadership",
            year=year,
            evaluation_questions=[
                EvaluationQuestion(
                    id="ceo-name",
                    question="Who is the CEO of Nirvana Retail Group?",
                    expected_answer=exec_dir["ceo_name"],
                    expected_sources=[exec_dir["document_id"]],
                    tags=["exact", "leadership"],
                ),
                EvaluationQuestion(
                    id="ceo-title",
                    question="What title does Krishna Turlapati hold at Nirvana Retail Group?",
                    expected_answer=exec_dir["ceo_title"],
                    expected_sources=[exec_dir["document_id"]],
                    tags=["exact", "leadership"],
                ),
                EvaluationQuestion(
                    id="ceo-doc-status",
                    question="What is the status of the executive leadership directory?",
                    expected_answer=exec_dir["status"],
                    expected_sources=[exec_dir["document_id"]],
                    tags=["policy"],
                ),
            ],
        )
    )

    return plans


def _filler_plan(
    company: dict[str, Any],
    gen: dict[str, Any],
    rng: random.Random,
    index: int,
    seed: int,
) -> DocumentPlan:
    regions = company["regions"]
    departments = company["departments"]
    products = company["products"]
    prefixes = gen.get("type_prefixes") or {}
    doc_types = ["policy", "procedure", "report", "runbook", "manual", "store_announcement"]
    doc_type = doc_types[index % len(doc_types)]
    region = regions[index % len(regions)]
    department = departments[index % len(departments)]
    product = products[index % len(products)]
    prefix = prefixes.get(doc_type, "DOC")
    doc_id = f"NRG-{prefix}-GOLD-{index:04d}"
    effective = f"2026-{(1 + index % 6):02d}-{(1 + index % 27):02d}"
    year = _year_from_date(effective)
    path = _raw_path(
        gen,
        doc_type,
        year,
        f"{index:03d}-{doc_type}-{region.lower().replace(' ', '-')}.md",
    )
    week = 1 + (index % 52)
    units = 80 + (index % 40)
    facts = {
        "document_id": doc_id,
        "region": region,
        "department": department,
        "product_code": product["code"],
        "product_name": product["name"],
        "week_number": str(week),
        "sample_units": str(units),
        "status": "approved",
        "version": "1.0",
    }
    return DocumentPlan(
        document_id=doc_id,
        title=f"{department} {doc_type.replace('_', ' ').title()} — {region} #{index}",
        document_type=doc_type,
        department=department,
        region=region,
        version="1.0",
        status="approved",
        effective_date=effective,
        expiry_date="",
        path=path,
        required_facts=facts,
        sections=_merge_sections(gen, doc_type, ["Summary", "Details", "Controls", "Contacts"]),
        seed=seed + index,
        corpus="gold",
        trap_tag="",
        year=year,
        evaluation_questions=[
            EvaluationQuestion(
                id=f"filler-{index}-sku",
                question=f"Which product code is referenced in {doc_id}?",
                expected_answer=product["code"],
                expected_sources=[doc_id],
                tags=["exact"],
            ),
            EvaluationQuestion(
                id=f"filler-{index}-region",
                question=f"Which region does {doc_id} cover?",
                expected_answer=region,
                expected_sources=[doc_id],
                tags=["exact"],
            ),
            EvaluationQuestion(
                id=f"filler-{index}-units",
                question=f"What sample_units value appears in {doc_id}?",
                expected_answer=str(units),
                expected_sources=[doc_id],
                tags=["exact"],
            ),
        ],
    )


def plan_gold(n: int, seed: int) -> list[DocumentPlan]:
    company = load_company_config()
    gen = load_generation_config()
    rng = random.Random(seed)
    plans = _gold_trap_plans(company, gen, seed)
    idx = 1
    while len(plans) < n:
        plans.append(_filler_plan(company, gen, rng, idx, seed))
        idx += 1
    return plans[:n]


def plan_scale(n: int, seed: int) -> list[DocumentPlan]:
    company = load_company_config()
    gen = load_generation_config()
    stores = list(company["stores"])
    weeks = int(gen.get("scale_weeks") or 50)
    doc_types = list(gen.get("scale_doc_types") or ["sales_weekly"])
    regions = company["regions"]
    products = company["products"]
    prefixes = gen.get("type_prefixes") or {}

    plans: list[DocumentPlan] = []
    i = 0
    for store in stores:
        for week in range(1, weeks + 1):
            for doc_type in doc_types:
                if i >= n:
                    return plans
                region = regions[i % len(regions)]
                product = products[i % len(products)]
                prefix = prefixes.get(doc_type, "RPT")
                doc_id = f"NRG-{prefix}-S{store}-W{week:02d}-{i:05d}"
                year = 2026
                path = _raw_path(
                    gen,
                    doc_type,
                    year,
                    f"store-{store}/w{week:02d}-{doc_type}.md",
                )
                units = 50 + ((i * 7) % 120)
                revenue = 10000 + ((i * 37) % 50000)
                facts = {
                    "document_id": doc_id,
                    "store_id": store,
                    "week_number": str(week),
                    "region": region,
                    "product_code": product["code"],
                    "units_sold": str(units),
                    "revenue_usd": str(revenue),
                    "status": "approved",
                    "version": "1.0",
                }
                plans.append(
                    DocumentPlan(
                        document_id=doc_id,
                        title=f"Store {store} {doc_type.replace('_', ' ').title()} Week {week}",
                        document_type=doc_type,
                        department="Store Operations",
                        region=region,
                        version="1.0",
                        status="approved",
                        effective_date="2026-01-01",
                        expiry_date="",
                        path=path,
                        required_facts=facts,
                        sections=_merge_sections(
                            gen, doc_type, ["Summary", "Metrics", "Notes", "Actions"]
                        ),
                        seed=seed + i,
                        corpus="scale",
                        trap_tag="",
                        year=year,
                    )
                )
                i += 1
    # If cartesian product is short, pad with extras
    while len(plans) < n:
        i = len(plans)
        store = stores[i % len(stores)]
        week = 1 + (i % weeks)
        doc_type = doc_types[i % len(doc_types)]
        region = regions[i % len(regions)]
        product = products[i % len(products)]
        prefix = prefixes.get(doc_type, "RPT")
        doc_id = f"NRG-{prefix}-PAD-{i:05d}"
        year = 2026
        path = _raw_path(gen, doc_type, year, f"pad/{i:05d}-{doc_type}.md")
        plans.append(
            DocumentPlan(
                document_id=doc_id,
                title=f"Pad {doc_type} {i}",
                document_type=doc_type,
                department="Store Operations",
                region=region,
                version="1.0",
                status="approved",
                effective_date="2026-01-01",
                expiry_date="",
                path=path,
                required_facts={
                    "document_id": doc_id,
                    "store_id": store,
                    "week_number": str(week),
                    "region": region,
                    "product_code": product["code"],
                    "units_sold": str(50 + i % 100),
                    "revenue_usd": str(10000 + i),
                    "status": "approved",
                    "version": "1.0",
                },
                sections=_merge_sections(gen, doc_type, ["Summary", "Metrics", "Notes"]),
                seed=seed + i,
                corpus="scale",
                trap_tag="",
                year=year,
            )
        )
    return plans[:n]


def write_plans(corpus: str, n: int, seed: int) -> Path:
    ensure_data_dirs(corpus)
    if corpus == "gold":
        plans = plan_gold(n, seed)
    elif corpus == "scale":
        plans = plan_scale(n, seed)
    else:
        raise ValueError(corpus)
    out = plans_path(corpus)
    _write_jsonl(out, plans)
    return out


def load_plans(corpus: str) -> list[DocumentPlan]:
    path = plans_path(corpus)
    if not path.exists():
        raise FileNotFoundError(f"No plans at {path}; run plan first")
    plans: list[DocumentPlan] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            plans.append(DocumentPlan.from_dict(json.loads(line)))
    return plans
