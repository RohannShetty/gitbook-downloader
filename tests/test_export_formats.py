"""Tests for real file exports (Markdown bundle, true PDF, and RAG JSONL)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from gitbook_downloader.gui.bridge import ApiBridge
from gitbook_downloader.storage.manager import StorageManager
from gitbook_downloader.utils.export import export_to_pdf


def test_export_to_pdf_generates_real_pdf(tmp_path: Path):
    """Verify that export_to_pdf creates a valid binary PDF with PDF header."""
    md_file = tmp_path / "test_doc.md"
    md_file.write_text(
        "# OpenCode Documentation\n\n"
        "Welcome to **OpenCode**.\n\n"
        "## Quickstart Guide\n\n"
        "Install via pip:\n\n"
        "```python\npip install opencode\n```\n\n"
        "- Feature 1: Fast crawling\n"
        "- Feature 2: Offline Markdown\n"
        "- Feature 3: RAG Ready\n\n"
        "### Conclusion\n\n"
        "Happy coding!\n",
        encoding="utf-8",
    )

    pdf_dest = tmp_path / "output.pdf"
    result_path = export_to_pdf(md_file, pdf_dest)

    assert Path(result_path).exists()
    assert Path(result_path).suffix == ".pdf"
    content = Path(result_path).read_bytes()
    assert len(content) > 500
    assert content.startswith(b"%PDF-")


def test_bridge_export_doc_all_formats(tmp_path: Path, monkeypatch):
    """Verify that ApiBridge.export_doc exports real files for md, pdf, and jsonl."""
    # Setup test domain in storage
    storage_dir = tmp_path / "library"
    monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path))
    storage = StorageManager(storage_dir)

    domain = "test.example.com"
    domain_dir = storage_dir / "docs" / domain
    domain_dir.mkdir(parents=True)
    
    # Create docs.md
    (domain_dir / "docs.md").write_text("# Test Docs\n\nSome content", encoding="utf-8")
    
    # Create pages
    pages_dir = domain_dir / "pages"
    pages_dir.mkdir(parents=True)
    (pages_dir / "page1.md").write_text("# Page 1\n\nDetails 1", encoding="utf-8")
    (pages_dir / "page2.md").write_text("# Page 2\n\nDetails 2", encoding="utf-8")

    bridge = ApiBridge(storage_manager=storage)
    export_dir = tmp_path / "exports"

    # 1. Test Markdown export
    res_md = bridge.export_doc(domain, "md", custom_path=str(export_dir))
    assert res_md.get("success") is True, f"res_md error: {res_md}"
    assert Path(res_md["path"]).exists()
    assert Path(res_md["path"]).read_text(encoding="utf-8") == "# Test Docs\n\nSome content"

    # 2. Test PDF export
    res_pdf = bridge.export_doc(domain, "pdf", custom_path=str(export_dir))
    assert res_pdf["success"] is True
    assert Path(res_pdf["path"]).exists()
    assert Path(res_pdf["path"]).read_bytes().startswith(b"%PDF-")

    # 3. Test JSONL export
    res_jsonl = bridge.export_doc(domain, "jsonl", custom_path=str(export_dir))
    assert res_jsonl["success"] is True
    assert Path(res_jsonl["path"]).exists()
    lines = Path(res_jsonl["path"]).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    record1 = json.loads(lines[0])
    assert record1["domain"] == domain
    assert "text" in record1
