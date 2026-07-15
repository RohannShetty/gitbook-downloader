"""gitbook-downloader v6.0 — Multi-provider documentation downloader."""

__version__ = "6.0.0"
__author__ = "Rohan Shetty"

from .utils import (
    create_session, retry_get, load_config, merge_config,
    init_default_config, normalize_url, is_md_url,
    wrap_with_rag_metadata, export_to_jsonl, export_to_pdf,
)
from .storage import StorageManager, VersionManager
from .providers import (
    Provider, ProviderRegistry, detect_provider, get_provider, list_providers,
    GitBookProvider, DocusaurusProvider, ReadTheDocsProvider,
    MintlifyProvider, GenericProvider,
)

__all__ = [
    "__version__",
    "StorageManager", "VersionManager",
    "detect_provider", "get_provider", "list_providers",
    "create_session", "load_config",
]
