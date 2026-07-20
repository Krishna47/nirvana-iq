"""Build and persist document manifests and evaluation indexes."""

from __future__ import annotations

from pathlib import Path

from .exporters import evaluation_payload, sha256_file_bytes, write_json, write_manifest_csv
from .models import EvaluationQuestion, GeneratedDocument, ManifestEntry


class ManifestBuilder:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.manifests_dir = output_dir / "manifests"
        self.evaluation_dir = output_dir / "evaluation"
        self.entries: list[ManifestEntry] = []
        self.questions: list[EvaluationQuestion] = []

    def add_document(self, document: GeneratedDocument, absolute_path: Path) -> ManifestEntry:
        digest = sha256_file_bytes(absolute_path.read_bytes())
        entry = ManifestEntry(
            document_id=document.plan.document_id,
            title=document.plan.title,
            department=document.plan.department,
            document_type=document.plan.document_type.value,
            region=document.plan.region,
            version=document.plan.version,
            status=document.plan.status,
            effective_date=document.plan.effective_date,
            expiry_date=document.plan.expiry_date,
            confidentiality=document.plan.confidentiality,
            owner=document.plan.owner,
            year=document.plan.year,
            path=str(Path(document.relative_path).as_posix()),
            sha256=digest,
            word_count=document.word_count,
            product_codes=list(document.plan.product_codes),
            keywords=list(document.plan.keywords),
        )
        self.entries.append(entry)
        self.questions.extend(document.plan.evaluation_questions)
        return entry

    def write(self) -> None:
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            self.manifests_dir / "documents.json",
            [entry.model_dump(mode="json") for entry in self.entries],
        )
        write_manifest_csv(self.manifests_dir / "documents.csv", self.entries)
        write_json(self.evaluation_dir / "questions.json", evaluation_payload(self.questions))
