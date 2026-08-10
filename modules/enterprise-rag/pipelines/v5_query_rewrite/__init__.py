"""v5 — Query rewrite package."""

from .pipeline import VERSION, QueryRewritePipeline, build_pipeline

Pipeline = QueryRewritePipeline

__all__ = ["VERSION", "Pipeline", "QueryRewritePipeline", "build_pipeline"]
