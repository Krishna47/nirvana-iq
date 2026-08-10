"""FastAPI surface for Nirvana IQ Enterprise RAG Evolution Lab."""

from __future__ import annotations

import sys
from pathlib import Path

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODULE_ROOT = Path(__file__).resolve().parents[1]
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from pipelines.registry import get_pipeline, list_versions  # noqa: E402
from shared.contracts import run_pipeline  # noqa: E402
from shared.conversation import ChatMessage as ConvMessage  # noqa: E402
from shared.conversation import normalize_history  # noqa: E402
from shared.corpus import find_documents_by_id  # noqa: E402
from shared.settings import load_env  # noqa: E402

load_env()

app = FastAPI(title="Nirvana IQ Enterprise RAG", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessageModel(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    version: str = "v1_basic_rag"
    messages: list[ChatMessageModel] = Field(
        default_factory=list,
        description="Prior conversation turns (not including the current question).",
    )


class CompareRequest(BaseModel):
    question: str = Field(min_length=1)
    versions: list[str] = Field(default_factory=lambda: ["v1_basic_rag"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/versions")
def versions() -> dict[str, list[str]]:
    return {"versions": list_versions()}


@app.get("/documents/{document_id}")
def get_document(
    document_id: str,
    status: str | None = Query(default=None, description="Filter by status, e.g. approved|expired"),
    version: str | None = Query(default=None, description="Filter by doc version, e.g. 2.0"),
    document_type: str | None = Query(
        default=None,
        description="Filter by type, e.g. policy|procedure|report",
    ),
    include_text: bool = Query(default=True, description="Include full markdown body"),
) -> dict:
    """Fetch gold corpus document(s) by document_id.

    The same id can appear more than once (e.g. NRG-POL-SALES-001 v1 expired + v2 approved).
    """
    matches = find_documents_by_id(
        document_id,
        status=status,
        version=version,
        document_type=document_type,
        include_text=include_text,
    )
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No documents found for document_id={document_id!r}",
        )
    return {
        "document_id": document_id,
        "count": len(matches),
        "documents": matches,
    }


@app.post("/ask")
def ask(body: AskRequest) -> dict:
    try:
        pipeline = get_pipeline(body.version)
    except SystemExit as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    history: list[ConvMessage] = normalize_history(
        [{"role": m.role, "content": m.content} for m in body.messages]
    )
    result = run_pipeline(pipeline, body.question, history=history)
    return result.to_dict()


@app.post("/compare")
def compare(body: CompareRequest) -> dict:
    rows = []
    for version in body.versions:
        try:
            pipeline = get_pipeline(version)
        except SystemExit as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result = run_pipeline(pipeline, body.question)
        rows.append(
            {
                "version": result.version,
                "answer": result.answer,
                "citations": result.citations,
                "latency_ms": result.latency_ms,
                "notes": result.notes,
            }
        )
    return {"question": body.question, "rows": rows}
