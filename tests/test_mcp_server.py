"""Tests for the MCP server — download_docs facade routing + error surfacing.

The server's only engine contact is ``server._run_capture(url, options_kwargs)``
(single injection seam). These tests monkeypatch that seam with a fake facade,
so no network and no real engine are involved.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

pytest.importorskip("mcp")

from gitbook_downloader.mcp import server


# ── Fakes ────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class FakeCaptureResult:
    """Field-for-field mimic of api.CaptureResult (plan §2 pinned contract)."""

    source_url: str = "https://docs.example.com"
    provider: str = "gitbook"
    site_versions_found: tuple = ()
    pages_captured: int = 0
    skipped: int = 0
    warnings: tuple = ()
    library_path: Optional[Path] = None
    local_path: Optional[Path] = None
    book_file: Optional[Path] = None
    manifest_file: Optional[Path] = None
    version_id: Optional[str] = None


class FakeCapture:
    """Callable fake: records kwargs, returns a preset result or raises."""

    def __init__(self, result=None, exc: Exception | None = None):
        self.calls: list[tuple[str, dict]] = []
        self._result = result if result is not None else FakeCaptureResult()
        self._exc = exc

    def __call__(self, url: str, options_kwargs: dict) -> Any:
        self.calls.append((url, options_kwargs))
        if self._exc is not None:
            raise self._exc
        return self._result


def call_tool(fn, **kwargs):
    """Invoke an async MCP tool function from sync test code."""
    return asyncio.run(fn(**kwargs))


@pytest.fixture()
def no_search(monkeypatch):
    """Neutralize the best-effort search re-index so fakes stay hermetic."""
    monkeypatch.setattr(server, "_search", None)


# ── download_docs: happy path ────────────────────────────────────────


def test_download_docs_happy_path_maps_result_fields(monkeypatch, no_search):
    result = FakeCaptureResult(
        source_url="https://docs.example.com/",
        provider="mintlify",
        site_versions_found=("v1", "v2"),
        pages_captured=42,
        skipped=7,
        warnings=("1 page had empty content",),
        library_path=Path("/lib/docs.example.com"),
        local_path=Path("./docs.example.com-docs"),
        book_file=Path("/lib/docs.example.com/book.md"),
        manifest_file=Path("/lib/docs.example.com/llms.txt"),
        version_id="snap-20260822",
    )
    fake = FakeCapture(result=result)
    monkeypatch.setattr(server, "_run_capture", fake)

    out = call_tool(server.download_docs, url="https://docs.example.com")

    assert "error" not in out
    assert out["url"] == "https://docs.example.com/"
    assert out["domain"] == "docs.example.com"
    assert out["provider"] == "mintlify"
    assert out["site_versions_found"] == ["v1", "v2"]
    assert out["pages_captured"] == 42
    assert out["skipped"] == 7
    assert out["warnings"] == ["1 page had empty content"]
    assert out["library_path"] == str(Path("/lib/docs.example.com"))
    assert out["local_path"] == str(Path("./docs.example.com-docs"))
    assert Path(out["book_file"]) == Path("/lib/docs.example.com/book.md")
    assert Path(out["manifest_file"]) == Path("/lib/docs.example.com/llms.txt")
    assert out["version_id"] == "snap-20260822"


def test_download_docs_none_result_paths_become_null(monkeypatch, no_search):
    """library/local mode fields that are absent must surface as null, not 'None'."""
    fake = FakeCapture(result=FakeCaptureResult(library_path=None, local_path=None))
    monkeypatch.setattr(server, "_run_capture", fake)

    out = call_tool(server.download_docs, url="https://www.docs.example.com")

    assert out["library_path"] is None
    assert out["local_path"] is None
    assert out["book_file"] is None
    assert out["manifest_file"] is None
    assert out["domain"] == "docs.example.com"  # www. stripped


# ── download_docs: honest parameter mapping onto CaptureOptions ─────


def test_download_docs_maps_params_onto_options_kwargs(monkeypatch, no_search):
    fake = FakeCapture()
    monkeypatch.setattr(server, "_run_capture", fake)

    call_tool(
        server.download_docs,
        url="https://docs.example.com",
        max_pages=100,
        workers=4,
        path_scope=["/api/", "/guide"],
        exclude_paths=["/forum*"],
        site_versions=["v2"],
        output_mode="local",
    )

    url, kwargs = fake.calls[0]
    assert url == "https://docs.example.com"
    assert kwargs["max_pages"] == 100
    assert kwargs["workers"] == 4
    assert kwargs["path_scope"] == ("/api/", "/guide")  # tuple per contract
    assert kwargs["exclude_paths"] == ("/forum*",)
    assert kwargs["site_versions"] == ("v2",)


def test_download_docs_defaults_are_contract_defaults(monkeypatch, no_search):
    """Omitted optionals must map to CaptureOptions defaults: unlimited pages,
    all versions, both outputs."""
    fake = FakeCapture()
    monkeypatch.setattr(server, "_run_capture", fake)

    call_tool(server.download_docs, url="https://docs.example.com")

    _, kwargs = fake.calls[0]
    assert kwargs["max_pages"] is None  # unlimited (NOT 0 — 0 is invalid now)
    assert kwargs["path_scope"] == ()
    assert kwargs["exclude_paths"] == ()
    assert kwargs["site_versions"] is None  # all detected versions
    assert kwargs["output_mode"] == "both"


# ── download_docs: error surfacing ───────────────────────────────────


def test_download_docs_surfaces_capture_errors(monkeypatch, no_search):
    fake = FakeCapture(exc=RuntimeError("boom: provider detection failed"))
    monkeypatch.setattr(server, "_run_capture", fake)

    out = call_tool(server.download_docs, url="https://docs.example.com")

    assert out == {"error": "boom: provider detection failed"}


def test_download_docs_surfaces_invalid_output_mode(monkeypatch, no_search):
    """An invalid output_mode must come back as an error, not a silent fallback."""
    fake = FakeCapture(exc=ValueError("output_mode must be one of: both, library, local"))
    monkeypatch.setattr(server, "_run_capture", fake)

    out = call_tool(
        server.download_docs, url="https://docs.example.com", output_mode="everywhere"
    )

    assert "error" in out
    assert "output_mode" in out["error"]


def test_facade_unavailable_is_reported_not_raised(monkeypatch, no_search):
    """If gitbook_downloader.api can't be imported, the tool reports it instead
    of crashing the server."""
    monkeypatch.setattr(server, "_default_capture", None)

    out = call_tool(server.download_docs, url="https://docs.example.com")

    assert "error" in out
    assert "not available" in out["error"]
    assert "pip install" in out["error"]


# ── search_docs: P7 fix — no phantom extra advertised ────────────────


def test_search_unavailable_message_points_at_real_fix(monkeypatch):
    monkeypatch.setattr(server, "_search", None)

    out = call_tool(server.search_docs, query="anything")

    assert len(out) == 1
    msg = out[0]["error"]
    assert "[search]" not in msg  # the empty placeholder extra must not be advertised
    assert "reinstall" in msg.lower()


# ── tool inventory: the other 7 tools remain registered ─────────────


def test_all_tools_registered():
    registered = {tool.name for tool in server.mcp._tool_manager.list_tools()}
    assert registered == {
        "download_docs",
        "search_docs",
        "list_domains",
        "find_docs",
        "get_doc",
        "read_doc",
        "diff_versions",
        "list_versions",
        "export_docs",
        "get_changelog",
        "query_doc_graph",
        "get_related_concepts",
    }


def test_search_docs_success(monkeypatch):
    mock_search = MagicMock()
    mock_search.search.return_value = [{"title": "Doc", "url": "https://example.com", "snippet": "Text"}]
    monkeypatch.setattr(server, "_search", mock_search)

    res = call_tool(server.search_docs, query="test", domain="example.com", limit=5)
    assert len(res) == 1
    assert res[0]["title"] == "Doc"


def test_list_domains_success(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.list_domains.return_value = [{"name": "example.com", "pages": 10}]
    monkeypatch.setattr(server, "_storage", mock_storage)

    res = call_tool(server.list_domains)
    assert len(res) == 1
    assert res[0]["name"] == "example.com"


# ── list_domains: storage-existence filter (DATA-3) ──────────────────


def test_list_domains_omits_domains_without_storage(tmp_path, monkeypatch):
    """Domains kept only by stale index/registry rows — with no docs.md on
    disk — must not surface through list_domains; a real domain stays listed.

    Mirrors the live data: the search index holds a domain (6,963 rows) whose
    ``docs/<domain>/`` directory no longer exists.
    """
    from gitbook_downloader.search import SearchIndex
    from gitbook_downloader.storage import StorageManager

    library = tmp_path / "library"
    storage = StorageManager(base_dir=library)
    monkeypatch.setattr(server, "_storage", storage)
    monkeypatch.setattr(server, "_search", SearchIndex(base_dir=library))

    # A real domain: book + metadata + index rows.
    storage.save_doc(
        domain="docs.real.com",
        content="# Real\n\nReal content.",
        url="https://docs.real.com/",
        title="Real",
        pages=2,
        provider="gitbook",
        new_pages=2,
        size_kb=0.2,
    )
    SearchIndex(base_dir=library).index_domain(
        "docs.real.com", "# Real\n\nReal content.", "https://docs.real.com/"
    )

    # Orphan A: search-index rows only, no storage directory at all.
    SearchIndex(base_dir=library).index_domain(
        "orphan-index.com",
        "# Orphan\n\nRows without storage.",
        "https://orphan-index.com/",
    )

    # Orphan B: a metadata registry entry whose docs.md is gone — the shape
    # StorageManager.list_domains() can actually surface and must be filtered.
    orphan_dir = storage._domain_dir("orphan-registry.com")
    orphan_dir.mkdir(parents=True)
    (orphan_dir / "metadata.json").write_text(
        json.dumps(
            {
                "domain": "orphan-registry.com",
                "title": "Orphan",
                "total_pages": 5,
                "latest_version": "1.0.0",
                "versions": [],
            }
        ),
        encoding="utf-8",
    )
    # Sanity: the orphan really does flow out of the raw storage listing.
    raw_names = [m.get("domain") for m in storage.list_domains()]
    assert "orphan-registry.com" in raw_names

    out = call_tool(server.list_domains)
    assert not any("error" in d for d in out)
    names = [d.get("domain") for d in out]
    assert "docs.real.com" in names
    assert "orphan-registry.com" not in names
    assert "orphan-index.com" not in names


def test_docstring_lists_every_registered_tool():
    """The module docstring must document exactly the registered tool set
    (regression: it once listed only 8 of the 12 tools)."""
    doc = server.__doc__ or ""
    registered = {tool.name for tool in server.mcp._tool_manager.list_tools()}
    assert len(registered) == 12
    for name in registered:
        assert name in doc, f"module docstring is missing tool {name!r}"


def test_get_doc_success(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.load_doc.return_value = "# Example Docs Content"
    mock_storage.get_metadata.return_value = {"latest_version": "v1.0"}
    monkeypatch.setattr(server, "_storage", mock_storage)

    res = call_tool(server.get_doc, domain="example.com")
    assert res["domain"] == "example.com"
    assert res["version"] == "v1.0"
    assert "Example Docs" in res["preview"]


def test_get_doc_not_found(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.load_doc.return_value = None
    mock_storage.get_metadata.return_value = None
    monkeypatch.setattr(server, "_storage", mock_storage)

    res = call_tool(server.get_doc, domain="missing.com")
    assert "error" in res


def test_diff_versions_success(monkeypatch):
    mock_versioning = MagicMock()
    mock_versioning.diff.return_value = "--- v1\n+++ v2\n+New line\n-Old line"
    monkeypatch.setattr(server, "_versioning", mock_versioning)

    res = call_tool(server.diff_versions, domain="example.com", v1="v1", v2="v2")
    assert res["domain"] == "example.com"
    assert res["added_lines"] == 1
    assert res["removed_lines"] == 1


def test_list_versions_success(monkeypatch):
    mock_versioning = MagicMock()
    mock_versioning.get_versions.return_value = [{"version": "v1.0"}, {"version": "v2.0"}]
    monkeypatch.setattr(server, "_versioning", mock_versioning)

    res = call_tool(server.list_versions, domain="example.com")
    assert len(res) == 2


def test_export_docs_markdown(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.load_doc.return_value = "# Markdown content"
    mock_storage.latest_path.return_value = Path("/tmp/example.md")
    monkeypatch.setattr(server, "_storage", mock_storage)

    res = call_tool(server.export_docs, domain="example.com", format="markdown")
    assert res["format"] == "markdown"
    assert "Markdown content" in res["preview"]


def test_export_docs_rag(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.load_doc.return_value = "# RAG doc content"
    monkeypatch.setattr(server, "_storage", mock_storage)

    res = call_tool(server.export_docs, domain="example.com", format="rag")
    assert res["format"] == "rag"
    assert "domain: example.com" in res["content"]


def test_export_docs_jsonl_writes_parseable_file(tmp_path, monkeypatch):
    """``export_docs(format="jsonl")`` must actually write the JSONL file.

    Regression: the tool passed the raw ``StorageManager`` to
    ``export_to_jsonl``, which requires a ``get_pages(domain)`` provider —
    the call hit the ``AttributeError`` path, logged an error, and silently
    wrote no file. The tool now wraps storage in ``StoragePageSource`` (the
    same adapter the CLI uses), so the JSONL lands on disk with one parseable
    record per stored page and frontmatter stripped from the payloads.
    """
    from gitbook_downloader.storage import StorageManager
    from gitbook_downloader.utils.export import StoragePageSource

    domain = "docs.example.com"
    storage = StorageManager(base_dir=tmp_path)
    monkeypatch.setattr(server, "_storage", storage)

    storage.save_doc(
        domain=domain,
        content="# Example\n\nCombined book content.",
        url="https://docs.example.com/",
        title="Example",
        pages=2,
        provider="gitbook",
    )
    pages_dir = storage._domain_dir(domain) / "pages"
    pages_dir.mkdir(parents=True)
    (pages_dir / "index.md").write_text(
        "---\n"
        "title: Home\n"
        "source_url: https://docs.example.com/\n"
        "---\n"
        "\n"
        "# Home\n"
        "\n"
        "Welcome to the documentation home page.",
        encoding="utf-8",
    )
    (pages_dir / "auth.md").write_text(
        "---\n"
        "title: Auth\n"
        "source_url: https://docs.example.com/auth\n"
        "---\n"
        "\n"
        "# Auth\n"
        "\n"
        "Authentication tokens and API keys.",
        encoding="utf-8",
    )
    # Sanity: the adapter sees the seeded pages through the real storage.
    assert len(StoragePageSource(storage, domain).get_pages(domain)) == 2

    res = call_tool(server.export_docs, domain=domain, format="jsonl")

    assert "error" not in res
    assert res["format"] == "jsonl"
    jsonl_path = Path(res["path"])
    assert jsonl_path.exists(), f"JSONL not written at {jsonl_path}"
    assert res["preview"], "preview must reflect the written file"

    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    records = [json.loads(line) for line in lines]  # every line parses
    assert {r["id"] for r in records} == {
        "https://docs.example.com/",
        "https://docs.example.com/auth",
    }
    for record in records:
        assert record["title"]
        assert record["text"].strip()
        assert record["metadata"]["domain"] == domain
        # Frontmatter must be stripped from the JSONL payload body.
        assert not record["text"].startswith("---")


def test_get_changelog_success(monkeypatch):
    mock_versioning = MagicMock()
    mock_versioning.changelog.return_value = [{"version": "v2.0", "added_lines": 5, "removed_lines": 2}]
    monkeypatch.setattr(server, "_versioning", mock_versioning)

    res = call_tool(server.get_changelog, domain="example.com")
    assert res["domain"] == "example.com"
    assert len(res["entries"]) == 1
    assert res["total_versions"] == 2


def test_query_doc_graph_and_related_concepts(tmp_path, monkeypatch):
    # Setup a mock domain with pages
    domain_dir = tmp_path / "graph_domain.com"
    pages_dir = domain_dir / "pages"
    pages_dir.mkdir(parents=True)

    page1 = pages_dir / "001_auth.md"
    page1.write_text(
        "# Authentication Guide\n\n## Overview\nUse JWT tokens.\n\nPOST /api/v1/login\n\nSee [Config](002_config.md)",
        encoding="utf-8"
    )

    page2 = pages_dir / "002_config.md"
    page2.write_text(
        "# Configuration\n\n## Settings\nSet JWT_SECRET environment variable.",
        encoding="utf-8"
    )

    mock_storage = MagicMock()
    mock_storage._domain_dir.return_value = domain_dir
    monkeypatch.setattr(server, "_storage", mock_storage)

    # Test query_doc_graph
    res = call_tool(server.query_doc_graph, domain="graph_domain.com", query="authentication")
    assert res["domain"] == "graph_domain.com"
    assert res["matches_count"] >= 1
    assert any("Authentication" in r["label"] for r in res["results"])

    # Test get_related_concepts
    res_concepts = call_tool(server.get_related_concepts, domain="graph_domain.com", concept="auth")
    assert res_concepts["domain"] == "graph_domain.com"
    assert "primary_matches" in res_concepts


