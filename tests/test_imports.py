"""Smoke tests — verify all modules import without errors."""

import sys
import subprocess
from pathlib import Path


def test_package_import():
    import gitbook_downloader
    assert gitbook_downloader.__version__ == "6.0.0"
    assert gitbook_downloader.StorageManager is not None


def test_utils_imports():
    from gitbook_downloader.utils import (
        create_session, load_config, normalize_url,
        discover_from_llms_txt, discover_from_sitemap,
        export_to_jsonl, wrap_with_rag_metadata,
    )


def test_providers_imports():
    from gitbook_downloader.providers import (
        Provider, ProviderRegistry, detect_provider,
        GitBookProvider, DocusaurusProvider, ReadTheDocsProvider,
        MintlifyProvider, GenericProvider,
    )
    names = ProviderRegistry.list_names()
    assert "gitbook" in names
    assert "generic" in names


def test_provider_registry_order():
    from gitbook_downloader.providers import list_providers
    names = list_providers()
    assert names == ["gitbook", "mintlify", "docusaurus", "readthedocs", "generic"]


def test_storage_imports():
    from gitbook_downloader.storage import StorageManager, VersionManager


def test_search_imports():
    from gitbook_downloader.search import SearchIndex


def test_mcp_imports():
    from gitbook_downloader.mcp import mcp, main
    assert hasattr(mcp, "tool")
    assert callable(mcp.tool)


def test_engine_imports():
    from gitbook_downloader.engine import stream_download, download_urls
    assert callable(stream_download)


def test_splitter():
    from gitbook_downloader.splitter import split_markdown, split_file
    assert callable(split_markdown)


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "gitbook_downloader.cli", "--help"],
        capture_output=True, text=True,
        cwd=Path(__file__).resolve().parent.parent,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower() or "download" in result.stdout.lower()
