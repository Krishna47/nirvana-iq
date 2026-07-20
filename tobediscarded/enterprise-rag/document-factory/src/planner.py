"""Deterministic factual planning — source of truth before LLM prose."""

from __future__ import annotations

import hashlib
import random
from collections import Counter
from datetime import date, timedelta
from typing import Any

from .config_loader import CompanyConfig, GenerationConfig
from .models import DocumentPlan, DocumentType, EvaluationQuestion


DEPT_ABBREV: dict[str, str] = {
    "Sales": "SALES",
    "Supply Chain": "SC",
    "Procurement": "PROC",
    "Finance": "FIN",
    "HR": "HR",
    "Information Security": "SEC",
    "Data Engineering": "DATA",
    "Cloud Operations": "CLOUD",
    "Customer Experience": "CX",
    "Legal": "LEGAL",
    "Merchandising": "MERCH",
    "Marketing": "MKT",
    "Store Operations": "STORE",
    "Compliance": "COMP",
}


class DocumentPlanner:
    """Build deterministic document plans from company and generation config."""

    def __init__(self, company: CompanyConfig, generation: GenerationConfig) -> None:
        self.company = company
        self.generation = generation
        self._type_to_class = {
            doc_type: class_name
            for class_name, types in generation.document_classes.items()
            for doc_type in types
        }

    def plan_documents(
        self,
        count: int,
        start_year: int,
        end_year: int,
        seed: int,
    ) -> list[DocumentPlan]:
        if start_year > end_year:
            raise ValueError("start_year must be <= end_year")
        if start_year < 2020 or end_year > 2026:
            raise ValueError("years must be within 2020-2026")
        if count < 1:
            raise ValueError("count must be >= 1")

        rng = random.Random(seed)
        type_queue = self._allocate_types(count, rng)
        years = list(range(start_year, end_year + 1))
        plans: list[DocumentPlan] = []
        used_ids: set[str] = set()

        for index, document_type in enumerate(type_queue, start=1):
            year = years[(index - 1) % len(years)]
            # Mild deterministic shuffle so years are not strictly round-robin per type.
            year = years[rng.randrange(0, len(years))] if rng.random() < 0.35 else year
            plan = self._build_plan(
                rng=rng,
                document_type=DocumentType(document_type),
                year=year,
                sequence=index,
                used_ids=used_ids,
            )
            plans.append(plan)
        return plans

    def _allocate_types(self, count: int, rng: random.Random) -> list[str]:
        weights = self.generation.document_type_weights
        total_weight = sum(weights.values())
        allocations: dict[str, int] = {}
        remainder_tokens: list[str] = []

        for doc_type, weight in weights.items():
            exact = (weight / total_weight) * count
            base = int(exact)
            allocations[doc_type] = base
            remainder_tokens.extend([doc_type] * max(1, int((exact - base) * 100)))

        assigned = sum(allocations.values())
        leftover = count - assigned
        if leftover > 0:
            pool = remainder_tokens or list(weights.keys())
            for _ in range(leftover):
                allocations[rng.choice(pool)] += 1
        elif leftover < 0:
            # Trim from largest buckets first for determinism.
            for doc_type, _ in sorted(allocations.items(), key=lambda item: (-item[1], item[0])):
                while leftover < 0 and allocations[doc_type] > 0:
                    allocations[doc_type] -= 1
                    leftover += 1

        queue: list[str] = []
        for doc_type, amount in sorted(allocations.items()):
            queue.extend([doc_type] * amount)
        rng.shuffle(queue)
        return queue[:count]

    def _build_plan(
        self,
        rng: random.Random,
        document_type: DocumentType,
        year: int,
        sequence: int,
        used_ids: set[str],
    ) -> DocumentPlan:
        department = rng.choice(self.company.departments)
        region = rng.choice(self.company.regions)
        products = rng.sample(self.company.products, k=rng.randint(1, min(3, len(self.company.products))))
        product_codes = [product.code for product in products]
        suppliers = sorted({product.supplier for product in products})
        if rng.random() < 0.4:
            extra = rng.choice(self.company.suppliers)
            if extra not in suppliers:
                suppliers.append(extra)
        systems = rng.sample(self.company.systems, k=rng.randint(1, min(3, len(self.company.systems))))
        owner = self.company.owners_by_department[department]
        status = self._choose_status(rng, year)
        confidentiality = rng.choice(self.company.confidentiality_levels)
        version = self._choose_version(rng, status)
        effective = date(year, rng.randint(1, 12), rng.randint(1, 28))
        published = effective - timedelta(days=rng.randint(7, 45))
        expiry: date | None
        if status == "expired":
            expiry = effective + timedelta(days=rng.randint(60, 180))
        elif document_type in {DocumentType.POLICY, DocumentType.CONTRACT, DocumentType.ANNOUNCEMENT}:
            expiry = effective + timedelta(days=rng.randint(90, 365)) if rng.random() < 0.55 else None
        else:
            expiry = None

        metrics = self._build_metrics(rng, document_type, products)
        title = self._build_title(document_type, region, department, products[0].name, year)
        document_id = self._make_document_id(document_type, department, sequence, used_ids)
        facts = self._build_facts(
            rng=rng,
            document_type=document_type,
            title=title,
            department=department,
            region=region,
            products=products,
            suppliers=suppliers,
            systems=systems,
            metrics=metrics,
            effective=effective,
            status=status,
        )
        evaluation_questions = self._build_eval_questions(document_id, facts, metrics, products)
        keywords = self._build_keywords(document_type, department, region, products)
        word_min, word_max = self._word_bounds(document_type.value)
        required_sections = self._required_sections(document_type.value)

        return DocumentPlan(
            document_id=document_id,
            title=title,
            document_type=document_type,
            year=year,
            department=department,
            region=region,
            version=version,
            status=status,
            confidentiality=confidentiality,
            owner=owner,
            effective_date=effective.isoformat(),
            expiry_date=expiry.isoformat() if expiry else None,
            published_date=published.isoformat(),
            product_codes=product_codes,
            suppliers=suppliers,
            systems=systems,
            metrics=metrics,
            facts=facts,
            keywords=keywords,
            evaluation_questions=evaluation_questions,
            required_sections=required_sections,
            word_min=word_min,
            word_max=word_max,
        )

    def _make_document_id(
        self,
        document_type: DocumentType,
        department: str,
        sequence: int,
        used_ids: set[str],
    ) -> str:
        prefix = self.generation.type_prefixes[document_type.value]
        dept = DEPT_ABBREV.get(department, "GEN")
        candidate = f"NRG-{prefix}-{dept}-{sequence:04d}"
        # Deterministic collision avoidance if department abbreviations collide.
        salt = 0
        while candidate in used_ids:
            salt += 1
            digest = hashlib.sha1(f"{candidate}-{salt}".encode()).hexdigest()[:4].upper()
            candidate = f"NRG-{prefix}-{dept}-{sequence:04d}{digest}"
        used_ids.add(candidate)
        return candidate

    def _choose_status(self, rng: random.Random, year: int) -> str:
        if year <= 2022:
            return rng.choice(["expired", "archived", "approved"])
        if year >= 2025:
            return rng.choice(["approved", "approved", "draft"])
        return rng.choice(["approved", "expired", "draft"])

    def _choose_version(self, rng: random.Random, status: str) -> str:
        major = rng.randint(1, 4)
        minor = rng.randint(0, 3)
        if status == "expired":
            major = max(1, major - 1)
        return f"{major}.{minor}"

    def _word_bounds(self, document_type: str) -> tuple[int, int]:
        class_name = self._type_to_class[document_type]
        bounds = self.generation.word_counts[class_name]
        return bounds["min"], bounds["max"]

    def _required_sections(self, document_type: str) -> list[str]:
        common = list(self.generation.required_sections.get("common", []))
        specific = list(self.generation.required_sections.get("by_type", {}).get(document_type, []))
        seen: set[str] = set()
        result: list[str] = []
        for heading in ["Executive Summary", *specific, *[h for h in common if h != "Executive Summary"]]:
            if heading not in seen:
                seen.add(heading)
                result.append(heading)
        return result

    def _build_title(
        self,
        document_type: DocumentType,
        region: str,
        department: str,
        product_name: str,
        year: int,
    ) -> str:
        templates: dict[DocumentType, list[str]] = {
            DocumentType.POLICY: [
                f"{region} {product_name} Promotion Policy",
                f"{department} Inventory Control Policy",
                f"{region} Returns and Exchanges Policy",
            ],
            DocumentType.PROCEDURE: [
                f"Supplier Delay Response Procedure for {region}",
                f"{department} Replenishment Procedure",
                f"{product_name} Intake Procedure",
            ],
            DocumentType.REPORT: [
                f"Q{((year % 4) + 1)} {year} {region} Sales Performance Report",
                f"{year} {department} Inventory Risk Report",
                f"{region} Omnichannel Conversion Report {year}",
            ],
            DocumentType.RUNBOOK: [
                f"{department} Pricing Engine Failover Runbook",
                f"Inventory Service Degradation Runbook",
                f"Customer Portal Incident Runbook",
            ],
            DocumentType.INCIDENT_REPORT: [
                f"{year} {region} Inventory Sync Incident Report",
                f"Pricing Engine Outage Incident — {region}",
                f"{product_name} Fulfillment Delay Incident",
            ],
            DocumentType.MEETING_MINUTES: [
                f"{department} Weekly Operations Meeting Minutes",
                f"{region} Merchandising Alignment Meeting",
                f"Supplier Performance Review Meeting — {year}",
            ],
            DocumentType.CONTRACT: [
                f"Master Supply Agreement Summary — {product_name}",
                f"Logistics Service Contract Summary — {region}",
                f"Component Supply Contract Overview {year}",
            ],
            DocumentType.PRODUCT_CATALOG: [
                f"{year} {region} Electronics Product Catalog",
                f"{product_name} Assortment Catalog",
                f"Omnichannel Product Catalog — {department}",
            ],
            DocumentType.ARCHITECTURE_DOCUMENT: [
                f"Retail Data Platform Architecture — {year}",
                f"Order Management Integration Architecture",
                f"{department} Systems Architecture Overview",
            ],
            DocumentType.ANNOUNCEMENT: [
                f"{region} Store Policy Update Announcement",
                f"{product_name} Launch Readiness Announcement",
                f"{department} Operating Change Announcement {year}",
            ],
        }
        choices = templates[document_type]
        # Stable across processes (avoid Python's randomized hash()).
        digest = hashlib.sha1(
            f"{document_type.value}:{region}:{department}:{product_name}:{year}".encode("utf-8")
        ).hexdigest()
        return choices[int(digest[:8], 16) % len(choices)]

    def _build_metrics(
        self,
        rng: random.Random,
        document_type: DocumentType,
        products: list[Any],
    ) -> dict[str, Any]:
        base = {
            "sla_hours": rng.choice([4, 8, 12, 24]),
            "reorder_point_units": rng.choice([50, 75, 100, 125, 150]),
            "discount_percent": rng.choice([5, 8, 10, 12, 15]),
            "target_fill_rate_percent": rng.choice([92, 95, 97, 98]),
            "max_return_window_days": rng.choice([14, 15, 30]),
            "uptime_recovery_minutes": rng.choice([15, 30, 45, 60]),
            "units_impacted": rng.choice([120, 250, 480, 900, 1500]),
            "revenue_impact_usd": rng.choice([25000, 48000, 125000, 310000]),
            "contract_value_usd": rng.choice([500000, 1250000, 2800000, 4500000]),
            "list_price_usd": {
                product.code: rng.choice([499, 699, 899, 1099, 1299, 1599, 1899])
                for product in products
            },
        }
        if document_type == DocumentType.REPORT:
            base["yoy_change_percent"] = rng.choice([-12, -8, -3, 2, 5, 9, 14])
            base["conversion_rate_percent"] = rng.choice([2.1, 2.8, 3.4, 4.0, 4.7])
        return base

    def _build_facts(
        self,
        rng: random.Random,
        document_type: DocumentType,
        title: str,
        department: str,
        region: str,
        products: list[Any],
        suppliers: list[str],
        systems: list[str],
        metrics: dict[str, Any],
        effective: date,
        status: str,
    ) -> dict[str, Any]:
        primary = products[0]
        shared = {
            "company_name": self.company.company_name,
            "headquarters": f"{self.company.headquarters.city}, {self.company.headquarters.state}",
            "title_theme": title,
            "primary_product_code": primary.code,
            "primary_product_name": primary.name,
            "primary_supplier": primary.supplier,
            "audience": f"{department} teams in {region}",
            "systems_in_scope": systems,
            "suppliers_in_scope": suppliers,
            "immutable_metrics": {
                "sla_hours": metrics["sla_hours"],
                "reorder_point_units": metrics["reorder_point_units"],
                "discount_percent": metrics["discount_percent"],
                "target_fill_rate_percent": metrics["target_fill_rate_percent"],
                "max_return_window_days": metrics["max_return_window_days"],
            },
            "escalation_path": [
                f"{department} On-Call Lead",
                self.company.owners_by_department[department],
                "Executive Operations Desk",
            ],
            "review_cycle_months": rng.choice([3, 6, 12]),
            "control_example": (
                f"Orders for {primary.code} below the reorder point of "
                f"{metrics['reorder_point_units']} sellable units must open a replenishment ticket "
                f"in {systems[0]} within {metrics['sla_hours']} hours."
            ),
            "exception_rule": (
                f"Exceptions require written approval from {self.company.owners_by_department[department]} "
                f"and must be logged in {systems[0]} within one business day."
            ),
        }

        type_facts: dict[str, Any]
        if document_type == DocumentType.POLICY:
            type_facts = {
                "policy_statement": (
                    f"{region} locations may apply a {metrics['discount_percent']}% promotional discount "
                    f"to {primary.code} while status is {status}."
                ),
                "scope_channels": ["store", "customer_portal", "marketplace"],
            }
        elif document_type == DocumentType.PROCEDURE:
            type_facts = {
                "prerequisites": [
                    f"Access to {systems[0]}",
                    f"Confirmed supplier contact at {suppliers[0]}",
                ],
                "step_count": rng.randint(5, 8),
                "trigger": f"Supplier ETA slip greater than {metrics['sla_hours']} hours for {primary.code}",
            }
        elif document_type == DocumentType.REPORT:
            type_facts = {
                "period_label": f"{effective.strftime('%B %Y')}",
                "headline_metric": (
                    f"{region} conversion rate was {metrics.get('conversion_rate_percent')}% "
                    f"with YoY change of {metrics.get('yoy_change_percent')}%."
                ),
                "units_sold": metrics["units_impacted"],
            }
        elif document_type == DocumentType.RUNBOOK:
            type_facts = {
                "trigger": f"{systems[0]} error rate above 5% for 10 minutes",
                "rollback_objective_minutes": metrics["uptime_recovery_minutes"],
                "primary_system": systems[0],
            }
        elif document_type == DocumentType.INCIDENT_REPORT:
            type_facts = {
                "incident_start": f"{effective.isoformat()}T09:15:00-05:00",
                "incident_end": f"{effective.isoformat()}T11:40:00-05:00",
                "severity": f"P{rng.choice([1, 2, 3])}",
                "root_cause": f"Stale cache in {systems[0]} after schema change",
                "units_impacted": metrics["units_impacted"],
                "revenue_impact_usd": metrics["revenue_impact_usd"],
            }
        elif document_type == DocumentType.MEETING_MINUTES:
            type_facts = {
                "meeting_date": effective.isoformat(),
                "attendees": [
                    owner_name
                    for owner_name in [
                        self.company.owners_by_department[department],
                        "Regional Operations Manager",
                        "Category Analyst",
                    ]
                ],
                "decision": (
                    f"Maintain {metrics['discount_percent']}% discount on {primary.code} "
                    f"through the current review cycle."
                ),
                "action_owner": self.company.owners_by_department[department],
            }
        elif document_type == DocumentType.CONTRACT:
            type_facts = {
                "counterparty": suppliers[0],
                "term_months": rng.choice([12, 24, 36]),
                "contract_value_usd": metrics["contract_value_usd"],
                "sla_fill_rate_percent": metrics["target_fill_rate_percent"],
                "penalty_percent": rng.choice([1, 2, 3]),
            }
        elif document_type == DocumentType.PRODUCT_CATALOG:
            type_facts = {
                "listed_products": [
                    {
                        "code": product.code,
                        "name": product.name,
                        "category": product.category,
                        "supplier": product.supplier,
                        "list_price_usd": metrics["list_price_usd"][product.code],
                    }
                    for product in products
                ],
                "availability_rule": (
                    f"Items below {metrics['reorder_point_units']} sellable units are marked limited stock."
                ),
            }
        elif document_type == DocumentType.ARCHITECTURE_DOCUMENT:
            type_facts = {
                "primary_system": systems[0],
                "dependent_systems": systems[1:] or [self.company.systems[0]],
                "rpo_minutes": rng.choice([5, 15, 30]),
                "rto_minutes": metrics["uptime_recovery_minutes"],
            }
        else:  # announcement
            type_facts = {
                "effective_change": (
                    f"Effective {effective.isoformat()}, {region} stores apply "
                    f"{metrics['discount_percent']}% off {primary.code}."
                ),
                "channels": ["associate app", "store bulletin", "intranet"],
                "support_contact": self.company.owners_by_department[department],
            }

        return {**shared, **type_facts}

    def _build_eval_questions(
        self,
        document_id: str,
        facts: dict[str, Any],
        metrics: dict[str, Any],
        products: list[Any],
    ) -> list[EvaluationQuestion]:
        primary = products[0]
        q1 = EvaluationQuestion(
            id=f"{document_id}-Q1",
            question=f"What is the reorder point for {primary.code}?",
            expected_answer=f"{metrics['reorder_point_units']} sellable units",
            expected_sources=[document_id],
        )
        q2 = EvaluationQuestion(
            id=f"{document_id}-Q2",
            question=f"What promotional discount applies to {primary.code}?",
            expected_answer=f"{metrics['discount_percent']}%",
            expected_sources=[document_id],
        )
        q3_answer = str(facts.get("exception_rule") or facts.get("decision") or facts.get("effective_change"))
        q3 = EvaluationQuestion(
            id=f"{document_id}-Q3",
            question="What exception or approval rule applies?",
            expected_answer=q3_answer,
            expected_sources=[document_id],
        )
        return [q1, q2, q3]

    def _build_keywords(
        self,
        document_type: DocumentType,
        department: str,
        region: str,
        products: list[Any],
    ) -> list[str]:
        return [
            self.company.company_name,
            document_type.value,
            department,
            region,
            products[0].code,
            products[0].name,
        ]


def summarize_type_distribution(plans: list[DocumentPlan]) -> dict[str, int]:
    return dict(Counter(plan.document_type.value for plan in plans))
