"""DocHarvest (gitbook-downloader) v11.0.0 — Modern shadcn/ui Desktop & CLI documentation harvesting platform."""

__version__ = "11.0.0"
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
    MintlifyProvider, NextraProvider, VitePressProvider, MkDocsProvider,
    ReadMeProvider, GenericProvider,
)

__all__ = [
    "__version__",
    "StorageManager", "VersionManager",
    "detect_provider", "get_provider", "list_providers",
    "create_session", "load_config",
    "GitBookProvider", "DocusaurusProvider", "ReadTheDocsProvider",
    "MintlifyProvider", "NextraProvider", "VitePressProvider",
    "MkDocsProvider", "ReadMeProvider", "GenericProvider",
]
