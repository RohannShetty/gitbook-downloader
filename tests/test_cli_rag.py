"""CLI ``--rag`` / ``--pdf`` post-capture exports — real end-to-end behavior.

The ``--rag`` block once imported ``export_to_jsonl``, printed the path and
never called the function (and referenced an undefined ``base_out``). These
tests drive the REAL CLI path: a fake engine is injected through the facade
seams (``api._load_stream_download`` / ``api._default_storage``), the real
``api.capture`` runs, the real output contract is written, and the JSONL/PDF
files are inspected on disk. No network, ever.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gitbook_downloader import api, cli
from gitbook_downloader.storage import StorageManager

PAGES = [
    {
        "url": "https://docs.example.com/",
        "title": "Home",
        "content": "# Home\n\nWelcome to the documentation home page.",
        "site_version": "",
    },
    {
        "url": "https://docs.example.com/guide/auth",
        "title": "Auth",
        "content": "# Auth\n\nAuthentication tokens and API keys.",
        "site_version": "",
    },
]


class FakeEngine:
    """Stands in for engine.stream_download (recorded, offline)."""

    def __init__(self, pages=PAGES):
        self.pages = pages
        self.calls: list[dict] = []

    def __call__(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        return {
            "pages": self.pages,
            "provider": "gitbook",
            "discovered": len(self.pages),
            "failed": 0,
        }


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Temp CWD + temp library, wired into the facade via its seams."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path / "library"))
    manager = StorageManager(base_dir=tmp_path / "library")
    monkeypatch.setattr(api, "_default_storage", lambda: manager)
    return tmp_path


@pytest.fixture
def fake_engine(monkeypatch):
    engine = FakeEngine()
    monkeypatch.setattr(api, "_load_stream_download", lambda: engine)
    return engine


def _printed_rag_path(capsys) -> Path:
    out = capsys.readouterr().out
    printed = [ln for ln in out.splitlines() if "RAG JSONL:" in ln]
    assert printed, f"CLI must print the RAG JSONL path on success; got:\n{out}"
    return Path(printed[0].split("RAG JSONL:")[1].strip())


# ── --rag: writes the JSONL for real ─────────────────────────────────


class TestRagExport:
    def test_rag_flag_writes_parseable_jsonl(self, tmp_path, capsys, fake_engine):
        rc = cli.main(["capture", "https://docs.example.com/", "--rag"])

        assert rc == 0
        rag_path = _printed_rag_path(capsys)
        assert rag_path.exists(), f"JSONL not written at printed path {rag_path}"

        lines = rag_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == len(PAGES)
        records = [json.loads(line) for line in lines]  # every line parses
        assert {r["id"] for r in records} == {p["url"] for p in PAGES}
        for record in records:
            assert record["title"]
            assert record["text"].strip()
            assert record["metadata"]["domain"] == "docs.example.com"
            # Frontmatter must be stripped from the RAG payload body.
            assert not record["text"].startswith("---")

    def test_rag_flag_prefers_existing_exports_dir(self, tmp_path, capsys, fake_engine):
        exports = tmp_path / "docs.example.com-docs" / "exports"
        exports.mkdir(parents=True)

        assert cli.main(["capture", "https://docs.example.com/", "--rag"]) == 0

        rag_path = _printed_rag_path(capsys)
        assert rag_path.parent == exports
        assert rag_path.exists()
        assert rag_path.name == "docs.example.com_rag.jsonl"

    def test_rag_failure_prints_warning_and_no_path(
        self, tmp_path, monkeypatch, capsys, fake_engine
    ):
        def broken_export(*args, **kwargs):
            raise RuntimeError("disk exploded")

        monkeypatch.setattr("gitbook_downloader.utils.export.export_to_jsonl", broken_export)

        rc = cli.main(["capture", "https://docs.example.com/", "--rag"])

        assert rc == 0  # export failure must not fail a successful capture
        captured = capsys.readouterr()
        assert "RAG export failed" in captured.err
        assert "RAG JSONL:" not in captured.out  # path printed on success only

    def test_no_rag_flag_writes_nothing(self, tmp_path, capsys, fake_engine):
        assert cli.main(["capture", "https://docs.example.com/"]) == 0
        out = capsys.readouterr().out
        assert "RAG JSONL" not in out
        assert not list(tmp_path.rglob("*_rag.jsonl"))

    def test_rag_with_zero_pages_writes_nothing(self, capsys, monkeypatch, fixture_server):
        # 0 pages: api.capture probes the source URL, so use the local
        # fixture server to keep the test fully offline.
        engine = FakeEngine(pages=[])
        monkeypatch.setattr(api, "_load_stream_download", lambda: engine)

        rc = cli.main(["capture", fixture_server.url("/"), "--rag"])

        assert rc == 1  # 0 pages captured → non-zero exit
        assert "RAG JSONL" not in capsys.readouterr().out


# ── --pdf: writes the handbook for real ──────────────────────────────


class TestPdfExport:
    def test_pdf_flag_writes_pdf_file(self, tmp_path, capsys, fake_engine):
        rc = cli.main(["capture", "https://docs.example.com/", "--pdf"])

        assert rc == 0
        out = capsys.readouterr().out
        printed = [ln for ln in out.splitlines() if "PDF Book:" in ln]
        assert printed, f"CLI must print the PDF path on success; got:\n{out}"
        pdf_path = Path(printed[0].split("PDF Book:")[1].strip())
        assert pdf_path.exists()
        assert pdf_path.read_bytes()[:4] == b"%PDF"

    def test_pdf_failure_prints_warning(self, tmp_path, monkeypatch, capsys, fake_engine):
        def broken_export(*args, **kwargs):
            raise RuntimeError("no fonts today")

        monkeypatch.setattr("gitbook_downloader.utils.export.export_to_pdf", broken_export)

        rc = cli.main(["capture", "https://docs.example.com/", "--pdf"])

        assert rc == 0
        captured = capsys.readouterr()
        assert "PDF export failed" in captured.err
        assert "PDF Book:" not in captured.out
