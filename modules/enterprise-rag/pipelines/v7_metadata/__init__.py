"""v7 — Metadata filters package."""

from .pipeline import VERSION, MetadataFilterPipeline, build_pipeline

Pipeline = MetadataFilterPipeline

__all__ = ["VERSION", "Pipeline", "MetadataFilterPipeline", "build_pipeline"]
