"""v6 — Multi-query package."""

from .pipeline import VERSION, MultiQueryPipeline, build_pipeline

Pipeline = MultiQueryPipeline

__all__ = ["VERSION", "Pipeline", "MultiQueryPipeline", "build_pipeline"]
