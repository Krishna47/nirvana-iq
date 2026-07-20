"""Enterprise RAG pipeline versions (interview ladder).

Layout mirrors:

  v1_basic_rag … v10_self_rag

Prefer adding a new version over mutating an old one.
"""

from .registry import get_pipeline, list_versions

__all__ = ["get_pipeline", "list_versions"]
