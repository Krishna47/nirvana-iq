"""v8 — Agentic RAG package."""

from .pipeline import VERSION, AgenticRagPipeline, build_pipeline

Pipeline = AgenticRagPipeline

__all__ = ["VERSION", "Pipeline", "AgenticRagPipeline", "build_pipeline"]
