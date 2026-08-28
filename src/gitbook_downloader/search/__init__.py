"""Search package — SQLite FTS5 full-text search and semantic concept graph."""

from .graph import DocGraph, build_graph_from_pages
from .index import SearchIndex

__all__ = ["SearchIndex", "DocGraph", "build_graph_from_pages"]
