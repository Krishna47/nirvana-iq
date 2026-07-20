"""Validate generated Markdown against plan facts and structural rules."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from .models import DocumentPlan


PRODUCT_CODE_RE = re.compile(r"\bNRG-[A-Z]{3}-\d{4}\b")
FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    word_count: int = 0
    content_hash: str = ""
    normalized_text: str = ""


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    body = FRONT_MATTER_RE.sub("", text, count=1)
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    tokens = re.findall(r"\b[\w'-]+\b", body)
    return len(tokens)


def extract_headings(markdown: str) -> list[str]:
    return [match.group(1).strip() for match in HEADING_RE.finditer(markdown)]


def similarity(a: str, b: str) -> float:
    """Jaccard similarity over normalized word sets."""
    set_a = set(normalize_text(a).split())
    set_b = set(normalize_text(b).split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


class DocumentValidator:
    def __init__(self, known_product_codes: set[str], similarity_threshold: float = 0.92) -> None:
        self.known_product_codes = known_product_codes
        self.similarity_threshold = similarity_threshold

    def validate(
        self,
        plan: DocumentPlan,
        markdown: str,
        existing_normalized: list[str] | None = None,
    ) -> ValidationResult:
        errors: list[str] = []
        if not FRONT_MATTER_RE.search(markdown):
            errors.append("Missing YAML front matter")

        headings = extract_headings(markdown)
        heading_lookup = {heading.lower(): heading for heading in headings}
        for required in plan.required_sections:
            if required.lower() not in heading_lookup:
                errors.append(f"Missing required section: {required}")

        # Immutable metadata must appear somewhere in the document.
        immutable_checks = {
            "document_id": plan.document_id,
            "version": plan.version,
            "department": plan.department,
            "region": plan.region,
            "status": plan.status,
            "confidentiality": plan.confidentiality,
            "effective_date": plan.effective_date,
        }
        for label, value in immutable_checks.items():
            if value and str(value) not in markdown:
                errors.append(f"Source fact missing from document: {label}={value}")

        for code in plan.product_codes:
            if code not in markdown:
                errors.append(f"Product code missing from document: {code}")

        metric_keys = [
            "reorder_point_units",
            "discount_percent",
            "sla_hours",
            "target_fill_rate_percent",
            "max_return_window_days",
        ]
        for key in metric_keys:
            value = plan.metrics.get(key)
            if value is None:
                continue
            # Accept numeric appearance with optional punctuation for percentages.
            needle = str(value)
            if needle not in markdown and f"{needle}%" not in markdown:
                errors.append(f"Metric missing from document: {key}={value}")

        unknown_codes = sorted(
            {
                code
                for code in PRODUCT_CODE_RE.findall(markdown)
                if code not in self.known_product_codes
            }
        )
        if unknown_codes:
            errors.append(f"Unknown product codes introduced: {', '.join(unknown_codes)}")

        for question in plan.evaluation_questions:
            if question.expected_answer and question.expected_answer not in markdown:
                # Allow date/number fragments when the answer is long.
                compact = question.expected_answer.strip()
                if len(compact) > 80:
                    tokens = [tok for tok in re.findall(r"\b\w+\b", compact) if len(tok) > 3][:6]
                    if tokens and not all(tok.lower() in markdown.lower() for tok in tokens[:3]):
                        errors.append(f"Expected answer not grounded for {question.id}")
                else:
                    errors.append(f"Expected answer not found for {question.id}: {question.expected_answer}")

        wc = word_count(markdown)
        if wc < plan.word_min or wc > plan.word_max:
            errors.append(
                f"Word count {wc} outside allowed range {plan.word_min}-{plan.word_max}"
            )

        normalized = normalize_text(markdown)
        digest = content_hash(markdown)
        if existing_normalized:
            for prior in existing_normalized:
                score = similarity(normalized, prior)
                if score >= self.similarity_threshold:
                    errors.append(f"Duplicate content detected (similarity={score:.3f})")
                    break

        return ValidationResult(
            ok=not errors,
            errors=errors,
            word_count=wc,
            content_hash=digest,
            normalized_text=normalized,
        )
