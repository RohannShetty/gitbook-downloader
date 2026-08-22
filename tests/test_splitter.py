"""Tests for markdown splitting (splitter module).

Covers:
  - split_markdown: core splitting logic
  - split_file: convenience wrapper
"""

import os
import tempfile
from pathlib import Path

import pytest

from gitbook_downloader.splitter import split_markdown, split_file


class TestSplitMarkdownBasic:
    """Tests for split_markdown core functionality."""

    def _make_sections(self, count=20):
        """Helper: create markdown with multiple # sections."""
        sections = []
        for i in range(count):
            sections.append(f"# Section {i}\n\nThis is content for section {i}.\n\n")
        return "\n".join(sections)

    def test_returns_list_of_tuples(self, tmp_path):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        assert isinstance(results, list)
        assert len(results) >= 1
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2
            filename, size = item
            assert isinstance(filename, str)
            assert isinstance(size, int)

    def test_creates_output_files(self, tmp_path):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        for filename, size in results:
            assert os.path.exists(filename)
            assert size > 0

    def test_creates_output_dir(self, tmp_path):
        md_content = self._make_sections(5)
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "nonexistent" / "chunks"
        assert not output_dir.exists()
        split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        assert output_dir.exists()

    def test_chunk_filenames_sequential(self, tmp_path):
        md_content = self._make_sections(10)
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        for i, (filename, _) in enumerate(results, 1):
            assert f"doc_part_{i:02d}.md" in filename

    def test_small_file_single_chunk(self, tmp_path):
        """A small file should produce a single chunk."""
        content = "# Short\n\nJust a little bit of content."
        input_path = tmp_path / "small.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=1.0)
        assert len(results) == 1

    def test_content_preserved(self, tmp_path):
        content = "# Header\n\nSome important content here."
        input_path = tmp_path / "input.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=1.0)
        filename = results[0][0]
        output_content = Path(filename).read_text(encoding="utf-8")
        assert "Header" in output_content
        assert "important content" in output_content


class TestSplitMarkdownCallback:
    """Tests for progress_callback parameter."""

    def test_callback_fires(self, tmp_path):
        callback_calls = []
        md_content = "\n".join(
            [f"# Section {i}\n\nContent for {i}.\n\n" for i in range(10)]
        )
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_cb"
        split_markdown(
            str(input_path), str(output_dir), max_mb=0.01,
            progress_callback=lambda d: callback_calls.append(d),
        )
        assert len(callback_calls) >= 1

    def test_callback_receive_correct_data(self, tmp_path):
        callback_calls = []
        md_content = "\n".join(
            [f"# Section {i}\n\nContent for {i}.\n\n" for i in range(10)]
        )
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_data"
        split_markdown(
            str(input_path), str(output_dir), max_mb=0.01,
            progress_callback=lambda d: callback_calls.append(d),
        )
        for call in callback_calls:
            assert call["phase"] == "chunk"
            assert "index" in call
            assert "total" in call
            assert "filename" in call
            assert isinstance(call["index"], int)
            assert isinstance(call["total"], int)

    def test_callback_index_increments(self, tmp_path):
        indices = []
        md_content = "\n".join(
            [f"# Section {i}\n\nContent for {i}.\n\n" for i in range(15)]
        )
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_idx"
        split_markdown(
            str(input_path), str(output_dir), max_mb=0.01,
            progress_callback=lambda d: indices.append(d["index"]),
        )
        assert indices == list(range(1, len(indices) + 1))


class TestSplitMarkdownMaxSize:
    """Tests for max_mb parameter."""

    def test_respects_max_size(self, tmp_path):
        """Chunks should not exceed max_mb (with some tolerance for header boundary)."""
        # Create content with known size
        big_section = "x" * 50000  # ~50KB
        md_content = f"# A\n\n{big_section}\n\n# B\n\n{big_section}\n\n# C\n\n{big_section}\n\n"
        input_path = tmp_path / "big.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_max"
        # max 60KB per chunk (each section is ~50KB)
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.06)
        for filename, size in results:
            # size is in bytes, max is 60KB = 61440 bytes
            # Allow some tolerance since we can't split within a section
            assert size <= 60000 + 50000  # worst case: one section slightly over + next header

    def test_many_chunks_when_small_max(self, tmp_path):
        """With a small max_mb, should produce multiple chunks."""
        # Each section ~200 bytes, 30 sections = ~6000 bytes
        # With max_mb=0.003 (~3KB), each chunk gets ~15 sections
        md_content = "\n".join(
            [f"# Section {i}\n\n{'Content ' * 20}{i}.\n\n" for i in range(30)]
        )
        input_path = tmp_path / "many.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_many"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.003)
        assert len(results) >= 2


class TestSplitMarkdownNoCallback:
    """Tests without callback (default behavior)."""

    def test_works_without_callback(self, tmp_path):
        md_content = "\n".join(
            [f"# Section {i}\n\nContent for {i}.\n\n" for i in range(10)]
        )
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        output_dir = tmp_path / "chunks_nocb"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        assert len(results) >= 1


# ════════════════════════════════════════════════════════════════
#  SPLIT FILE (convenience)
# ════════════════════════════════════════════════════════════════

class TestSplitFile:
    """Tests for split_file convenience function."""

    def _make_sections(self, count=20):
        sections = []
        for i in range(count):
            sections.append(f"# Section {i}\n\nContent for section {i}.\n\n")
        return "\n".join(sections)

    def test_creates_chunks(self, tmp_path):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        results = split_file(str(input_path), quiet=True)
        assert len(results) >= 1

    def test_default_output_dir(self, tmp_path):
        """Default output dir should be <input>_chunks."""
        md_content = self._make_sections()
        input_path = tmp_path / "docs.md"
        input_path.write_text(md_content, encoding="utf-8")
        results = split_file(str(input_path), quiet=True)
        # All files should be in docs_chunks/
        for filename, _ in results:
            assert "docs_chunks" in filename

    def test_custom_output_dir(self, tmp_path):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        custom_dir = tmp_path / "custom_output"
        results = split_file(str(input_path), output_dir=str(custom_dir), quiet=True)
        for filename, _ in results:
            assert str(custom_dir) in filename

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError, match="File not found"):
            split_file("/nonexistent/path.md")

    def test_quiet_mode(self, tmp_path, capsys):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        split_file(str(input_path), quiet=True)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_verbose_mode(self, tmp_path, capsys):
        md_content = self._make_sections()
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        split_file(str(input_path), quiet=False, max_mb=0.01)
        captured = capsys.readouterr()
        assert "Reading" in captured.out
        assert "Done!" in captured.out

    def test_max_mb_forwarded(self, tmp_path):
        # Each section ~200 bytes, 30 sections = ~6000 bytes
        md_content = "\n".join(
            [f"# Section {i}\n\n{'Content ' * 20}{i}.\n\n" for i in range(30)]
        )
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        results = split_file(str(input_path), max_mb=0.003, quiet=True)
        assert len(results) >= 2  # Should produce multiple chunks with small max

    def test_callback_forwarded(self, tmp_path):
        callback_calls = []
        md_content = self._make_sections(10)
        input_path = tmp_path / "input.md"
        input_path.write_text(md_content, encoding="utf-8")
        split_file(
            str(input_path),
            max_mb=0.01,
            quiet=True,
            progress_callback=lambda d: callback_calls.append(d),
        )
        assert len(callback_calls) >= 1


class TestSplitterEdgeCases:
    """Edge case tests for the splitter."""

    def test_no_headers(self, tmp_path):
        """Content without any headers should produce a single chunk."""
        content = "This is just plain text without any markdown headers."
        input_path = tmp_path / "no_headers.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=1.0)
        assert len(results) == 1

    def test_only_headers(self, tmp_path):
        """Content that's all headers with no body."""
        content = "# A\n# B\n# C\n"
        input_path = tmp_path / "headers.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=1.0)
        assert len(results) >= 1

    def test_unicode_content(self, tmp_path):
        """Content with unicode characters."""
        content = "# 日本語\n\nこれは日本語のコンテンツです。\n\n# 한국어\n\n한국어 콘텐츠입니다.\n"
        input_path = tmp_path / "unicode.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=1.0)
        assert len(results) >= 1
        # Verify content is preserved
        output_content = Path(results[0][0]).read_text(encoding="utf-8")
        assert "日本語" in output_content

    def test_code_blocks_not_split(self, tmp_path):
        """Large code block should stay in one chunk."""
        code = "```python\n" + "print('hello')\n" * 100 + "```\n"
        content = f"# Intro\n\nSome text.\n\n# Code\n\n{code}\n"
        input_path = tmp_path / "code.md"
        input_path.write_text(content, encoding="utf-8")
        output_dir = tmp_path / "chunks"
        results = split_markdown(str(input_path), str(output_dir), max_mb=0.01)
        # The code block should be in one chunk, not split
        for filename, _ in results:
            file_content = Path(filename).read_text(encoding="utf-8")
            if "print" in file_content:
                assert file_content.count("```") <= 2  # opening and closing
