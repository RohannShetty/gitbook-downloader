"""Tests for the Desktop GUI ApiBridge and assets."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gitbook_downloader.gui.app import get_web_dir
from gitbook_downloader.gui.bridge import ApiBridge


def test_get_web_dir_exists():
    web_dir = get_web_dir()
    assert web_dir.exists()
    assert (web_dir / "index.html").exists()
    assert (web_dir / "assets").exists() or (web_dir / "app.js").exists()


def test_bridge_detect_invalid_url():
    bridge = ApiBridge()
    res = bridge.detect("not-a-url")
    assert res["success"] is False
    assert "valid" in res["error"].lower()


def test_bridge_detect_mocked(monkeypatch):
    class FakeProvider:
        name = "gitbook"
        evidence = "mock evidence"

        def discover_urls(self, url):
            return ["https://docs.example.com/v1/a", "https://docs.example.com/v2/b"]

    monkeypatch.setattr(
        "gitbook_downloader.gui.bridge.detect_provider",
        lambda url, sess: FakeProvider(),
    )
    bridge = ApiBridge()
    res = bridge.detect("https://docs.example.com/")
    assert res["success"] is True
    assert res["provider"] == "gitbook"
    assert "v1" in res["site_versions"]
    assert "v2" in res["site_versions"]


def test_bridge_system_info():
    bridge = ApiBridge()
    info = bridge.get_system_info()
    assert info["version"] == "11.0.4"
    assert info["name"] == "DocHarvest"
    assert "DocHarvest Engine" in info["engine"]
    assert info["author"] == "Rohan Shetty"
    assert info["platform"] == sys.platform
    assert Path(info["library_dir"]).exists()
    render_status = bridge.is_render_available()
    assert "available" in render_status


def test_bridge_cancel_capture():
    bridge = ApiBridge()
    res = bridge.cancel_capture()
    assert res["success"] is True
    assert bridge._cancel_requested is True


def test_bridge_diagnostics_empty():
    bridge = ApiBridge()
    diag = bridge.get_diagnostics()
    assert diag == {}


def test_bridge_search_empty():
    bridge = ApiBridge()
    hits = bridge.search_docs("")
    assert hits == []


def test_bridge_list_library():
    bridge = ApiBridge()
    entries = bridge.list_library()
    assert isinstance(entries, list)


def test_bridge_rename_domain(tmp_path):
    from gitbook_downloader.storage import StorageManager
    sm = StorageManager(base_dir=tmp_path)
    sm.save_doc(domain="test.domain", content="# Content", url="u", title="T", pages=1, provider="generic", new_pages=1, size_kb=1.0)
    bridge = ApiBridge(storage_manager=sm)

    res = bridge.rename_domain("test.domain", "renamed.domain")
    assert res["success"] is True
    assert res["domain"] == "renamed.domain"
    assert sm.domain_exists("renamed.domain")
    assert not sm.domain_exists("test.domain")


def test_bridge_export_doc_not_found(tmp_path):
    bridge = ApiBridge()
    res = bridge.export_doc("non-existent-domain", "md", custom_path=str(tmp_path))
    assert res["success"] is False
    assert "not found" in res["error"].lower()
