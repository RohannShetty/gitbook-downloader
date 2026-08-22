"""FakeEngine behaviour — canned results, scripted progress, call log."""

from __future__ import annotations

import pytest

from gitbook_downloader.tui.engine_protocol import (
    CaptureOptions,
    Detection,
    SearchHit,
)
from gitbook_downloader.tui.testing import FakeEngine


def test_capture_records_call_and_returns_canned_result():
    engine = FakeEngine()
    options = CaptureOptions(path_scope=("/api/",), snapshot=False)
    events = []
    result = engine.capture(
        "https://docs.example.com", options, progress=events.append
    )
    assert result.provider == "mintlify"
    assert result.pages_captured == 42
    assert result.version_id is None  # snapshot disabled -> no snapshot id
    assert ("capture", ("https://docs.example.com", options)) in [
        (name, args) for name, args, _ in engine.calls
    ]


def test_capture_scripts_full_progress_timeline():
    engine = FakeEngine()
    events = []
    engine.capture("https://docs.example.com", CaptureOptions(), progress=events.append)
    kinds = [e.kind for e in events]
    assert kinds[0] == "discovered"
    assert "failed" in kinds  # one scripted failure mid-run
    assert kinds[-1] == "written"
    downloaded = [e for e in events if e.kind == "downloaded"]
    assert downloaded[0].done == 1 and downloaded[-1].done == downloaded[-1].total


def test_capture_error_surfaces_verbatim():
    engine = FakeEngine(capture_error=RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        engine.capture("https://docs.example.com", CaptureOptions())


def test_detect_returns_canned_detection():
    engine = FakeEngine()
    detection = engine.detect("https://docs.example.com")
    assert detection == Detection(
        provider="mintlify", evidence="generator meta tag", site_versions=("v1", "v2")
    )


def test_detect_error_propagates():
    engine = FakeEngine(detect_error=ValueError("nope"))
    with pytest.raises(ValueError, match="nope"):
        engine.detect("https://docs.example.com")


def test_search_filters_by_query_then_domain_then_limit():
    engine = FakeEngine()
    hits = engine.search("workers", limit=50)
    assert len(hits) == 3
    scoped = engine.search("workers", domain="api.other.dev", limit=50)
    assert [h.domain for h in scoped] == ["api.other.dev"]
    limited = engine.search("workers", limit=1)
    assert len(limited) == 1
    assert all(isinstance(h, SearchHit) for h in hits)
    assert "<b>workers</b>" in hits[0].snippet  # highlight markers preserved


def test_list_library_and_delete_domain():
    engine = FakeEngine()
    domains = [e.domain for e in engine.list_library()]
    assert domains == ["docs.example.com", "api.other.dev"]
    assert engine.delete_domain("docs.example.com") is True
    assert [e.domain for e in engine.list_library()] == ["api.other.dev"]
    assert engine.delete_domain("missing.example") is False


def test_snapshots_are_newest_first_and_diff_is_canned():
    engine = FakeEngine()
    snaps = engine.list_snapshots("docs.example.com")
    assert [s.version_id for s in snaps] == ["v1.1.0", "v1.0.1", "v1.0.0"]
    report = engine.diff_snapshots("docs.example.com", "v1.0.1", "v1.1.0")
    statuses = sorted(c.status for c in report.changes)
    assert statuses == ["added", "changed", "changed", "removed"]
    assert report.unchanged_pages == 35
