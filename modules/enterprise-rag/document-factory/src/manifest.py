"""Build documents.jsonl / JSON / CSV manifests with SHA-256 checksums."""

from __future__ import annotations

import json
from pathlib import Path

from .config_loader import corpus_root, ensure_data_dirs
from .exporters import sha256_file, write_csv_manifest, write_generation_summary
from .models import ManifestRecord
from .planner import load_plans
from .status import corpus_status


def write_manifest(corpus: str) -> Path:
    ensure_data_dirs(corpus)
    root = corpus_root(corpus)
    plans = load_plans(corpus)
    out = root / "manifests" / "documents.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    records: list[ManifestRecord] = []
    with out.open("w", encoding="utf-8") as handle:
        for plan in plans:
            path = root / plan.path
            if not path.exists():
                continue
            record = ManifestRecord(
                document_id=plan.document_id,
                title=plan.title,
                document_type=plan.document_type,
                department=plan.department,
                region=plan.region,
                version=plan.version,
                status=plan.status,
                effective_date=plan.effective_date,
                expiry_date=plan.expiry_date,
                path=plan.path,
                sha256=sha256_file(path),
                trap_tag=plan.trap_tag,
                confidentiality=plan.confidentiality,
                metadata={
                    "corpus": corpus,
                    "required_facts": plan.required_facts,
                    "year": plan.year,
                },
            )
            records.append(record)
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    if not records:
        raise FileNotFoundError(f"No generated files found under {root}; run generate first")

    json_path = root / "manifests" / "documents.json"
    json_path.write_text(
        json.dumps([r.to_dict() for r in records], indent=2),
        encoding="utf-8",
    )
    write_csv_manifest(records, root / "manifests" / "documents.csv")

    st = corpus_status(corpus)
    write_generation_summary(
        corpus,
        planned=int(st["planned"]),
        written=int(st["written"]),
        skipped=0,
        failed=int(st.get("generate_error_files") or 0),
        extra={"manifest_count": len(records)},
    )
    return out
