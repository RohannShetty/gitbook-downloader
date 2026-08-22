"""Utility modules for GitBook Downloader v6."""

from .retry import create_session, retry_get, TimeoutHTTPAdapter, DEFAULT_TIMEOUT
from .config import load_config, merge_config, init_default_config, DEFAULTS
from .discovery import discover_from_llms_txt, discover_from_sitemap, normalize_url, is_md_url
from .export import wrap_with_rag_metadata, export_to_jsonl, export_to_pdf

__all__ = [
    "create_session", "retry_get", "TimeoutHTTPAdapter", "DEFAULT_TIMEOUT",
    "load_config", "merge_config", "init_default_config", "DEFAULTS",
    "discover_from_llms_txt", "discover_from_sitemap", "normalize_url", "is_md_url",
    "wrap_with_rag_metadata", "export_to_jsonl", "export_to_pdf",
]
