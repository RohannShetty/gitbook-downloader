"""Contract tests — the TUI mirror must match the pinned facade exactly.

These run WITHOUT textual: pure dataclass/protocol checks against plan §2.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

from gitbook_downloader.tui.engine_protocol import (
    PROGRESS_KINDS,
    CaptureOptions,
    CaptureResult,
    EngineProtocol,
    ProgressEvent,
)
from gitbook_downloader.tui.testing import FakeEngine

# ── Pinned contract (plan §2) ────────────────────────────────────────────

PINNED_OPTIONS_FIELDS = [
    ("workers", 8),
    ("max_pages", None),
    ("path_scope", ()),
    ("exclude_paths", ()),
    ("site_versions", None),
    ("output_mode", "both"),
    ("local_dir", None),
    ("snapshot", True),
    ("timeout", 20.0),
]

PINNED_RESULT_FIELDS = [
    "source_url",
    "provider",
    "site_versions_found",
    "pages_captured",
    "skipped",
    "warnings",
    "library_path",
    "local_path",
    "book_file",
    "manifest_file",
    "version_id",
]


def test_capture_options_mirror_matches_pinned_contract():
    fields = [(f.name, f.default) for f in dataclasses.fields(CaptureOptions)]
    assert fields == PINNED_OPTIONS_FIELDS


def test_capture_result_mirror_matches_pinned_contract():
    names = [f.name for f in dataclasses.fields(CaptureResult)]
    assert names == PINNED_RESULT_FIELDS


def test_capture_options_and_result_are_frozen():
    assert dataclasses.is_dataclass(CaptureOptions)
    assert dataclasses.is_dataclass(CaptureResult)
    opts = CaptureOptions()
    with pytest.raises(dataclasses.FrozenInstanceError):
        opts.workers = 4  # type: ignore[misc]
    result = CaptureResult(
        source_url="u",
        provider="generic",
        site_versions_found=(),
        pages_captured=0,
        skipped=0,
        warnings=(),
        library_path=None,
        local_path=None,
        book_file=None,
        manifest_file=None,
        version_id=None,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.provider = "x"  # type: ignore[misc]


def test_progress_event_kinds_match_pinned_vocabulary():
    assert PROGRESS_KINDS == ("discovered", "downloaded", "failed", "written")
    event = ProgressEvent(kind="discovered")
    assert event.url == "" and event.done == 0 and event.total == 0


def test_fake_engine_satisfies_engine_protocol():
    assert isinstance(FakeEngine(), EngineProtocol)


def _fresh_import(module_name: str):
    """Import a module with all project/textual entries purged; return the
    set of newly-added top-level module names."""
    before = set(sys.modules)
    for mod in list(sys.modules):
        if mod.startswith(("gitbook_downloader", "textual")):
            del sys.modules[mod]
    import importlib

    importlib.import_module(module_name)
    return {m.split(".")[0] for m in set(sys.modules) - before}


def test_engine_protocol_module_imports_no_textual():
    """The contract layer must never pull textual.

    Note: the repo root ``gitbook_downloader/__init__.py`` (v6 legacy,
    outside TUI write scope) eagerly imports providers/utils, so
    transitive stdlib/backend roots appear regardless; we assert on what
    the TUI layers themselves control.
    """
    saved = dict(sys.modules)
    try:
        new_top_level = _fresh_import("gitbook_downloader.tui.engine_protocol")
        new_top_level |= _fresh_import("gitbook_downloader.tui.testing")

        assert "textual" not in new_top_level
        assert "gitbook_downloader.api" not in sys.modules
        # Only tui-owned submodules may be newly imported.
        unexpected = {
            m
            for m in new_top_level
            if m.startswith("gitbook_downloader.")
            and not m.startswith("gitbook_downloader.tui")
        }
        assert unexpected == set(), unexpected
    finally:
        sys.modules.clear()
        sys.modules.update(saved)


def test_real_engine_module_is_lazy_about_backends():
    """real_engine must not import the api facade (or textual) at module
    scope; backend imports happen only inside method bodies at launch."""
    saved = dict(sys.modules)
    try:
        new_top_level = _fresh_import("gitbook_downloader.tui.real_engine")

        assert "textual" not in new_top_level
        assert "gitbook_downloader.api" not in sys.modules

        # Constructing the adapter still imports nothing heavy.
        from gitbook_downloader.tui.real_engine import RealEngine

        RealEngine()
        assert "gitbook_downloader.api" not in sys.modules

        # Static laziness contract: backend/textual imports may only live
        # inside function bodies, never at module top level.
        import ast
        import inspect

        from gitbook_downloader.tui import app as app_mod
        from gitbook_downloader.tui import real_engine as engine_mod

        forbidden_roots = ("requests", "textual")
        forbidden_full = {
            "gitbook_downloader.api",
            "gitbook_downloader.storage.manager",
            "gitbook_downloader.search.index",
            "gitbook_downloader.providers",
        }

        def assert_lazy(mod, roots):
            tree = ast.parse(inspect.getsource(mod))
            for node in tree.body:
                if isinstance(node, ast.Import):
                    targets = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    targets = [node.module or ""]
                else:
                    continue
                for target in targets:
                    assert target not in forbidden_full, (mod, target)
                    assert target.split(".")[0] not in roots, (mod, target)

        # The adapter: no requests/textual/backends at module scope.
        assert_lazy(engine_mod, forbidden_roots)
        # The app shell may own textual, but still no backend imports.
        assert_lazy(app_mod, ("requests",))
    finally:
        sys.modules.clear()
        sys.modules.update(saved)


def test_tui_package_import_does_not_pull_textual():
    saved = dict(sys.modules)
    try:
        before = set(sys.modules)
        for mod in list(sys.modules):
            if mod.startswith(("gitbook_downloader", "textual")):
                del sys.modules[mod]
        import gitbook_downloader.tui as tui_pkg  # noqa: F401

        assert "textual" not in set(sys.modules) - before
        # Lazy attribute access works and only then pulls textual.
        app_cls = tui_pkg.GitbookDownloaderApp
        assert app_cls is not None
        assert "textual" in sys.modules
    finally:
        sys.modules.clear()
        sys.modules.update(saved)


def test_capture_run_defaults_allow_failed_runs():
    from gitbook_downloader.tui.engine_protocol import CaptureRun

    run = CaptureRun(
        url="https://x.example",
        options=CaptureOptions(),
        detection=None,
        result=None,
        error="boom",
    )
    assert run.event_counts == {}
    assert run.duration_s == 0.0
    assert run.result is None
