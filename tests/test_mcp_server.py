"""Tests for the MCP server — download_docs facade routing + error surfacing.

The server's only engine contact is ``server._run_capture(url, options_kwargs)``
(single injection seam). These tests monkeypatch that seam with a fake facade,
so no network and no real engine are involved.
"""

from __future__ import annotations

import asyncio
import dataclasses
from pathlib import Path
from typing import Any, Optional

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


def test_all_eight_tools_registered():
    registered = {tool.name for tool in server.mcp._tool_manager.list_tools()}
    assert registered == {
        "download_docs",
        "search_docs",
        "list_domains",
        "get_doc",
        "diff_versions",
        "list_versions",
        "export_docs",
        "get_changelog",
    }
