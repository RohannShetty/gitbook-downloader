"""Tests for utility modules (retry, config, discovery, export).

Covers:
  - retry.py: create_session, retry_get, TimeoutHTTPAdapter, DEFAULT_TIMEOUT
  - config.py: load_config, merge_config, init_default_config, DEFAULTS
  - discovery.py: normalize_url, is_md_url, discover_from_llms_txt, discover_from_sitemap
  - export.py: wrap_with_rag_metadata, export_to_jsonl, export_to_pdf
"""

import ast
import json
import os
import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gitbook_downloader.utils import (
    create_session, retry_get, TimeoutHTTPAdapter, DEFAULT_TIMEOUT,
    load_config, merge_config, init_default_config, DEFAULTS,
    normalize_url, is_md_url,
    discover_from_llms_txt, discover_from_sitemap,
    wrap_with_rag_metadata, export_to_jsonl, export_to_pdf,
)


# ════════════════════════════════════════════════════════════════
#  RETRY MODULE
# ════════════════════════════════════════════════════════════════

class TestTimeoutHTTPAdapter:
    """Tests for TimeoutHTTPAdapter."""

    def test_default_timeout(self):
        adapter = TimeoutHTTPAdapter()
        assert adapter.timeout == DEFAULT_TIMEOUT

    def test_custom_timeout(self):
        adapter = TimeoutHTTPAdapter(timeout=42)
        assert adapter.timeout ==42

    def test_default_timeout_value(self):
        assert DEFAULT_TIMEOUT == 20

    def test_timeout_none_uses_default(self):
        adapter = TimeoutHTTPAdapter(timeout=None)
        assert adapter.timeout == DEFAULT_TIMEOUT


class TestCreateSession:
    """Tests for create_session factory."""

    def test_returns_session(self):
        session = create_session()
        assert session is not None
        assert hasattr(session, "get")

    def test_user_agent_set(self):
        session = create_session()
        assert "User-Agent" in session.headers
        assert "Mozilla" in session.headers["User-Agent"]

    def test_custom_user_agent(self):
        session = create_session(user_agent="TestBot/1.0")
        assert session.headers["User-Agent"] == "TestBot/1.0"

    def test_custom_timeout(self):
        session = create_session(timeout=30)
        adapter = session.get_adapter("https://example.com")
        assert adapter.timeout == 30

    def test_session_has_retry_adapter(self):
        session = create_session()
        adapter = session.get_adapter("https://example.com")
        assert isinstance(adapter, TimeoutHTTPAdapter)

    def test_session_has_http_and_https(self):
        session = create_session()
        http_adapter = session.get_adapter("http://example.com")
        https_adapter = session.get_adapter("https://example.com")
        assert isinstance(http_adapter, TimeoutHTTPAdapter)
        assert isinstance(https_adapter, TimeoutHTTPAdapter)


class TestRetryGet:
    """Tests for retry_get helper."""

    def test_success_returns_tuple(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            resp, err = retry_get(session, "https://example.com")
            assert resp is mock_response
            assert err is None

    def test_timeout_returns_error(self):
        import requests as req
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_get.side_effect = req.Timeout("Connection timed out")
            resp, err = retry_get(session, "https://example.com")
            assert resp is None
            assert err == "Timeout"

    def test_connection_error_returns_error(self):
        import requests as req
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_get.side_effect = req.ConnectionError("DNS failed")
            resp, err = retry_get(session, "https://example.com")
            assert resp is None
            assert err == "Connection failed"

    def test_generic_exception_returns_truncated_msg(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_get.side_effect = ValueError("x" * 200)
            resp, err = retry_get(session, "https://example.com")
            assert resp is None
            assert err is not None
            assert len(err) <= 80

    def test_forwards_kwargs(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response
            retry_get(session, "https://example.com", timeout=5)
            mock_get.assert_called_once_with("https://example.com", timeout=5)


# ════════════════════════════════════════════════════════════════
#  CONFIG MODULE
# ════════════════════════════════════════════════════════════════

class TestConfigDefaults:
    """Tests for DEFAULTS dict."""

    def test_workers(self):
        assert DEFAULTS["workers"] == 5

    def test_timeout(self):
        assert DEFAULTS["timeout"] == 20

    def test_retry_attempts(self):
        assert DEFAULTS["retry_attempts"] == 3

    def test_max_pages(self):
        assert DEFAULTS["max_pages"] == 0

    def test_prefer_md(self):
        assert DEFAULTS["prefer_md"] is True

    def test_min_content_chars(self):
        assert DEFAULTS["min_content_chars"] == 60

    def test_use_llms_txt(self):
        assert DEFAULTS["use_llms_txt"] is True

    def test_output_dir(self):
        assert "gitbook-downloader" in DEFAULTS["output_dir"]


class TestMergeConfig:
    """Tests for merge_config."""

    def test_cli_overrides_file(self):
        file_config = {"workers": 3, "timeout": 10}
        cli_args = {"workers": 10, "max_pages": 100}
        merged = merge_config(cli_args, file_config)
        assert merged["workers"] == 10  # CLI wins
        assert merged["timeout"] == 10  # From file
        assert merged["max_pages"] == 100  # From CLI

    def test_none_values_skipped(self):
        file_config = {"workers": 5, "timeout": 20}
        cli_args = {"workers": None, "timeout": None}
        merged = merge_config(cli_args, file_config)
        assert merged["workers"] == 5
        assert merged["timeout"] == 20

    def test_empty_cli(self):
        file_config = {"workers": 5}
        merged = merge_config({}, file_config)
        assert merged["workers"] == 5

    def test_cli_adds_new_keys(self):
        file_config = {"workers": 5}
        cli_args = {"custom_key": "value"}
        merged = merge_config(cli_args, file_config)
        assert merged["custom_key"] == "value"
        assert merged["workers"] == 5

    def test_preserves_file_keys(self):
        file_config = {"a": 1, "b": 2, "c": 3}
        cli_args = {"a": 10}
        merged = merge_config(cli_args, file_config)
        assert merged["a"] == 10
        assert merged["b"] == 2
        assert merged["c"] == 3

    def test_boolean_override(self):
        """Boolean flags should be respected even when False."""
        file_config = {"prefer_md": True}
        cli_args = {"prefer_md": False}
        merged = merge_config(cli_args, file_config)
        assert merged["prefer_md"] is False


class TestInitDefaultConfig:
    """Tests for init_default_config."""

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            init_default_config(str(path))
            assert path.exists()

    def test_file_contains_download_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            init_default_config(str(path))
            content = path.read_text(encoding="utf-8")
            assert "[download]" in content
            assert "[output]" in content

    def test_file_contains_workers_comment(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            init_default_config(str(path))
            content = path.read_text(encoding="utf-8")
            assert "workers" in content
            assert "timeout" in content

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            init_default_config(str(path))
            mtime1 = path.stat().st_mtime
            init_default_config(str(path))  # Should not overwrite
            mtime2 = path.stat().st_mtime
            assert mtime1 == mtime2

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subdir" / "deep" / "config.toml"
            init_default_config(str(path))
            assert path.exists()

    def test_returns_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            result = init_default_config(str(path))
            assert os.path.isabs(result)


class TestLoadConfig:
    """Tests for load_config (no file → defaults)."""

    def test_no_config_returns_defaults(self):
        """When no config file exists, should return defaults."""
        config = load_config()
        assert isinstance(config, dict)
        assert "workers" in config
        assert config["workers"] == DEFAULTS["workers"]

    def test_returns_all_default_keys(self):
        config = load_config()
        for key in DEFAULTS:
            assert key in config


# ════════════════════════════════════════════════════════════════
#  DISCOVERY MODULE
# ════════════════════════════════════════════════════════════════

class TestNormalizeUrl:
    """Tests for normalize_url in utils."""

    def test_strips_fragment(self):
        result = normalize_url("https://example.com/page#section")
        assert "#" not in result
        assert result == "https://example.com/page"

    def test_strips_trailing_slash(self):
        assert normalize_url("https://example.com/page/") == "https://example.com/page"

    def test_strips_md_suffix(self):
        result = normalize_url("https://example.com/page.md")
        assert result == "https://example.com/page"

    def test_collapses_double_slashes(self):
        result = normalize_url("https://example.com//page//sub")
        assert "//" not in result.split("://", 1)[1]

    def test_preserves_query(self):
        result = normalize_url("https://example.com/page?foo=bar")
        assert "foo=bar" in result

    def test_simple_url_unchanged(self):
        url = "https://example.com/page"
        assert normalize_url(url) == url

    def test_root_url(self):
        result = normalize_url("https://example.com/")
        assert result == "https://example.com"


class TestIsMdUrl:
    """Tests for is_md_url."""

    def test_true_for_md_extension(self):
        assert is_md_url("https://example.com/page.md") is True

    def test_false_for_html(self):
        assert is_md_url("https://example.com/page.html") is False

    def test_false_for_no_extension(self):
        assert is_md_url("https://example.com/page") is False

    def test_case_insensitive(self):
        assert is_md_url("https://example.com/page.MD") is True
        assert is_md_url("https://example.com/page.Md") is True

    def test_empty_string(self):
        assert is_md_url("") is False

    def test_md_in_path_not_extension(self):
        assert is_md_url("https://example.com/.md-other") is False


class TestDiscoverFromLlmsTxt:
    """Tests for discover_from_llms_txt with mocked HTTP."""

    def test_returns_urls_from_markdown_links(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = (
                "# Docs\n\n"
                "[Page 1](https://docs.example.com/page1)\n"
                "[Page 2](https://docs.example.com/page2.md)\n"
                "[External](https://other.com/page3)\n"
            )
            mock_get.return_value = mock_resp
            urls = discover_from_llms_txt("https://docs.example.com", session)
            assert isinstance(urls, set)
            # Only same-domain URLs kept, and normalized (no .md suffix)
            assert "https://docs.example.com/page1" in urls
            assert "https://docs.example.com/page2" in urls
            assert not any("other.com" in u for u in urls)

    def test_returns_empty_set_on_error(self):
        session = create_session()
        with patch("gitbook_downloader.utils.discovery.retry_get") as mock_rg:
            mock_rg.return_value = (None, "Timeout")
            urls = discover_from_llms_txt("https://docs.example.com", session)
            assert urls == set()

    def test_returns_empty_set_on_404(self):
        session = create_session()
        with patch("gitbook_downloader.utils.discovery.retry_get") as mock_rg:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_rg.return_value = (mock_resp, None)
            urls = discover_from_llms_txt("https://docs.example.com", session)
            assert urls == set()

    def test_strips_trailing_slash_from_base(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = "[Page](https://docs.example.com/page)"
            mock_get.return_value = mock_resp
            urls = discover_from_llms_txt("https://docs.example.com/", session)
            assert len(urls) >= 1


class TestDiscoverFromSitemap:
    """Tests for discover_from_sitemap with mocked HTTP."""

    def test_returns_urls_from_xml(self):
        session = create_session()
        with patch("gitbook_downloader.utils.discovery.retry_get") as mock_rg:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = (
                '<?xml version="1.0"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                '  <url><loc>https://docs.example.com/page1</loc></url>\n'
                '  <url><loc>https://docs.example.com/page2</loc></url>\n'
                '</urlset>'
            )
            mock_rg.return_value = (mock_resp, None)
            urls = discover_from_sitemap("https://docs.example.com", session)
            assert isinstance(urls, set)
            assert "https://docs.example.com/page1" in urls
            assert "https://docs.example.com/page2" in urls

    def test_returns_empty_on_no_sitemap(self):
        session = create_session()
        with patch("gitbook_downloader.utils.discovery.retry_get") as mock_rg:
            mock_rg.return_value = (None, "Connection failed")
            urls = discover_from_sitemap("https://docs.example.com", session)
            assert urls == set()

    def test_filters_external_urls(self):
        session = create_session()
        with patch("gitbook_downloader.utils.discovery.retry_get") as mock_rg:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = (
                '<?xml version="1.0"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                '  <url><loc>https://docs.example.com/page1</loc></url>\n'
                '  <url><loc>https://other.com/page2</loc></url>\n'
                '</urlset>'
            )
            mock_rg.return_value = (mock_resp, None)
            urls = discover_from_sitemap("https://docs.example.com", session)
            assert all("docs.example.com" in u for u in urls)


# ════════════════════════════════════════════════════════════════
#  EXPORT MODULE
# ════════════════════════════════════════════════════════════════

class TestWrapWithRagMetadata:
    """Tests for wrap_with_rag_metadata."""

    def test_basic_wrap(self):
        result = wrap_with_rag_metadata(
            "Hello world",
            "example.com",
            url="https://example.com/page",
        )
        assert "<!-- domain: example.com" in result
        assert "Hello world" in result
        assert "source: https://example.com/page" in result

    def test_chunk_info(self):
        result = wrap_with_rag_metadata(
            "Content",
            "example.com",
            url="https://example.com/page",
            chunk_num=3,
            total_chunks=10,
        )
        assert "chunk: 3/10" in result

    def test_headings(self):
        result = wrap_with_rag_metadata(
            "Content",
            "example.com",
            url="https://example.com/page",
            headings=["Intro", "Setup", "API"],
        )
        assert "headings: [Intro, Setup, API]" in result

    def test_no_headings(self):
        result = wrap_with_rag_metadata(
            "Content",
            "example.com",
            url="https://example.com/page",
            headings=None,
        )
        assert "headings: [none]" in result

    def test_empty_headings(self):
        result = wrap_with_rag_metadata(
            "Content",
            "example.com",
            url="https://example.com/page",
            headings=[],
        )
        assert "headings: [none]" in result

    def test_content_preserved(self):
        content = "# Title\n\nSome **bold** text."
        result = wrap_with_rag_metadata(content, "dom", url="https://dom")
        assert "# Title" in result
        assert "**bold**" in result

    def test_metadata_comment_format(self):
        result = wrap_with_rag_metadata(
            "Body",
            "test.com",
            url="https://test.com/page",
            chunk_num=1,
            total_chunks=2,
        )
        # Should be an HTML comment followed by content
        assert result.startswith("<!--")
        assert result.endswith("Body")


class TestExportToJsonl:
    """Tests for export_to_jsonl."""

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock()
            mock_storage.get_pages.return_value = [
                {"url": "https://example.com/page1", "title": "Page 1", "content": "Hello 1"},
                {"url": "https://example.com/page2", "title": "Page 2", "content": "Hello 2"},
            ]
            output_path = Path(tmp) / "output.jsonl"
            export_to_jsonl("example.com", mock_storage, str(output_path))
            assert output_path.exists()

    def test_correct_line_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock()
            mock_storage.get_pages.return_value = [
                {"url": "https://example.com/p1", "title": "P1", "content": "C1"},
                {"url": "https://example.com/p2", "title": "P2", "content": "C2"},
                {"url": "https://example.com/p3", "title": "P3", "content": "C3"},
            ]
            output_path = Path(tmp) / "output.jsonl"
            export_to_jsonl("example.com", mock_storage, str(output_path))
            lines = output_path.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 3

    def test_json_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock()
            mock_storage.get_pages.return_value = [
                {"url": "https://example.com/p1", "title": "My Page", "content": "Content here"},
            ]
            output_path = Path(tmp) / "output.jsonl"
            export_to_jsonl("example.com", mock_storage, str(output_path))
            lines = output_path.read_text(encoding="utf-8").strip().split("\n")
            data = json.loads(lines[0])
            assert data["id"] == "https://example.com/p1"
            assert data["title"] == "My Page"
            assert data["text"] == "Content here"
            assert data["metadata"]["domain"] == "example.com"

    def test_empty_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock()
            mock_storage.get_pages.return_value = []
            output_path = Path(tmp) / "output.jsonl"
            export_to_jsonl("example.com", mock_storage, str(output_path))
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8").strip()
            assert content == ""

    def test_missing_get_pages_method(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock(spec=[])  # No methods
            output_path = Path(tmp) / "output.jsonl"
            # Should not raise, just log error
            export_to_jsonl("example.com", mock_storage, str(output_path))
            assert not output_path.exists()

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock_storage = MagicMock()
            mock_storage.get_pages.return_value = [
                {"url": "u", "title": "t", "content": "c"},
            ]
            output_path = Path(tmp) / "subdir" / "deep" / "output.jsonl"
            export_to_jsonl("example.com", mock_storage, str(output_path))
            assert output_path.exists()


class TestExportToPdf:
    """Tests for export_to_pdf."""

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            export_to_pdf("/nonexistent/file.md", "/tmp/output.pdf")

    def test_creates_html_fallback(self):
        """Without weasyprint, should create HTML file."""
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "test.md"
            md_path.write_text("# Hello\n\nWorld", encoding="utf-8")
            output_path = Path(tmp) / "output"
            result = export_to_pdf(str(md_path), str(output_path))
            # Should return a message about HTML fallback or PDF
            assert isinstance(result, str)
            # HTML file should exist (weasyprint unlikely in test env)
            html_path = Path(tmp) / "output.html"
            if html_path.exists():
                content = html_path.read_text(encoding="utf-8")
                assert "<h1>" in content
                assert "Hello" in content

    def test_html_content_conversion(self):
        """Test that markdown headings are converted to HTML."""
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "test.md"
            md_path.write_text(
                "# Title\n\n## Subtitle\n\nSome **bold** text.\n\n`code`",
                encoding="utf-8",
            )
            output_path = Path(tmp) / "output"
            export_to_pdf(str(md_path), str(output_path))
            html_path = Path(tmp) / "output.html"
            if html_path.exists():
                content = html_path.read_text(encoding="utf-8")
                assert "<h1>" in content
                assert "<h2>" in content
                assert "<strong>" in content
                assert "<code>" in content
