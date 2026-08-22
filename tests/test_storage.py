"""Tests for storage system — StorageManager and VersionManager.

All tests use temporary directories, never touching ~/.gitbook-downloader.
"""

import json
import tempfile
from pathlib import Path

import pytest

from gitbook_downloader.storage import StorageManager, VersionManager, VersioningError


# ════════════════════════════════════════════════════════════════
#  STORAGE MANAGER
# ════════════════════════════════════════════════════════════════

class TestStorageManagerInit:
    """Tests for StorageManager initialization."""

    def test_custom_base_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.base == Path(tmp).resolve()

    def test_base_is_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert isinstance(sm.base, Path)

    def test_domain_dir_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            ddir = sm._domain_dir("example.com")
            assert ddir == Path(tmp) / "docs" / "example.com"

    def test_metadata_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.metadata_path("test.com") == Path(tmp) / "docs" / "test.com" / "metadata.json"

    def test_latest_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.latest_path("test.com") == Path(tmp) / "docs" / "test.com" / "docs.md"

    def test_versions_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.versions_dir("test.com") == Path(tmp) / "docs" / "test.com" / "versions"

    def test_chunks_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.chunks_dir("test.com") == Path(tmp) / "docs" / "test.com" / "chunks"


class TestStorageManagerSaveAndLoad:
    """Tests for save_doc and load_doc."""

    @pytest.fixture
    def sm(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield StorageManager(base_dir=tmp)

    def test_save_creates_docs_md(self, sm):
        sm.save_doc(
            domain="test.com",
            content="# Hello World\n\nTest content.",
            url="https://test.com/",
            title="Test Docs",
            pages=5,
            provider="gitbook",
            new_pages=5,
            size_kb=1.5,
        )
        path = sm.latest_path("test.com")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "# Hello World\n\nTest content."

    def test_load_returns_content(self, sm):
        sm.save_doc(
            domain="test.com",
            content="# Docs\n\nBody text.",
            url="https://test.com/",
            title="Docs",
            pages=3,
            provider="generic",
            new_pages=3,
            size_kb=0.5,
        )
        content = sm.load_doc("test.com")
        assert content is not None
        assert "# Docs" in content
        assert "Body text." in content

    def test_load_nonexistent_returns_none(self, sm):
        content = sm.load_doc("nonexistent.example.com")
        assert content is None

    def test_save_creates_metadata(self, sm):
        sm.save_doc(
            domain="test.com",
            content="# Test",
            url="https://test.com/",
            title="Test",
            pages=3,
            provider="gitbook",
            new_pages=3,
            size_kb=0.5,
        )
        meta = sm.get_metadata("test.com")
        assert meta is not None
        assert meta["domain"] == "test.com"
        assert meta["url"] == "https://test.com/"
        assert meta["title"] == "Test"
        assert meta["provider"] == "gitbook"
        assert meta["total_pages"] == 3
        assert meta["total_size_kb"] == 0.5

    def test_save_creates_first_version(self, sm):
        sm.save_doc(
            domain="test.com",
            content="Content",
            url="https://test.com/",
            title="Test",
            pages=1,
            provider="generic",
            new_pages=1,
            size_kb=0.1,
        )
        meta = sm.get_metadata("test.com")
        assert meta["latest_version"] == "1.0.0"
        assert len(meta["versions"]) == 1
        assert meta["versions"][0]["version"] == "1.0.0"
        assert meta["versions"][0]["is_latest"] is True

    def test_save_creates_update_history(self, sm):
        sm.save_doc(
            domain="test.com",
            content="Content",
            url="https://test.com/",
            title="Test",
            pages=1,
            provider="generic",
            new_pages=1,
            size_kb=0.1,
        )
        meta = sm.get_metadata("test.com")
        assert len(meta["update_history"]) == 1
        assert meta["update_history"][0]["new_pages"] == 1

    def test_save_updates_existing(self, sm):
        sm.save_doc(domain="test.com", content="V1", url="u", title="T",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        sm.save_doc(domain="test.com", content="V2", url="u", title="T",
                     pages=2, provider="generic", new_pages=1, size_kb=0.2)
        meta = sm.get_metadata("test.com")
        assert meta["total_pages"] == 2
        assert meta["total_size_kb"] == 0.2
        assert len(meta["update_history"]) == 2

    def test_save_preserves_first_scraped(self, sm):
        sm.save_doc(domain="test.com", content="V1", url="u", title="T",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        meta1 = sm.get_metadata("test.com")
        first_scraped = meta1["first_scraped"]
        sm.save_doc(domain="test.com", content="V2", url="u", title="T",
                     pages=2, provider="generic", new_pages=1, size_kb=0.2)
        meta2 = sm.get_metadata("test.com")
        assert meta2["first_scraped"] == first_scraped


class TestStorageManagerDomainHelpers:
    """Tests for domain_exists, ensure_domain_dir, list_domains."""

    @pytest.fixture
    def sm(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield StorageManager(base_dir=tmp)

    def test_domain_exists_false_initially(self, sm):
        assert sm.domain_exists("test.com") is False

    def test_domain_exists_true_after_save(self, sm):
        sm.save_doc(domain="test.com", content="Content", url="u", title="T",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        assert sm.domain_exists("test.com") is True

    def test_ensure_domain_dir_creates_directory(self, sm):
        ddir = sm.ensure_domain_dir("test.com")
        assert ddir.exists()
        assert ddir.is_dir()

    def test_ensure_domain_dir_idempotent(self, sm):
        ddir1 = sm.ensure_domain_dir("test.com")
        ddir2 = sm.ensure_domain_dir("test.com")
        assert ddir1 == ddir2

    def test_list_domains_empty(self, sm):
        domains = sm.list_domains()
        assert isinstance(domains, list)
        assert len(domains) == 0

    def test_list_domains_after_saves(self, sm):
        sm.save_doc(domain="alpha.com", content="A", url="u", title="A",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        sm.save_doc(domain="beta.com", content="B", url="u", title="B",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        domains = sm.list_domains()
        names = [d["domain"] for d in domains]
        assert "alpha.com" in names
        assert "beta.com" in names

    def test_delete_domain(self, sm):
        sm.save_doc(domain="test.com", content="Content", url="u", title="T",
                     pages=1, provider="generic", new_pages=1, size_kb=0.1)
        assert sm.delete_domain("test.com") is True
        assert sm.domain_exists("test.com") is False

    def test_delete_nonexistent_domain(self, sm):
        assert sm.delete_domain("nonexistent.com") is False


class TestStorageManagerTotalSize:
    """Tests for get_total_size."""

    def test_empty_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            assert sm.get_total_size() == 0

    def test_total_after_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            sm.save_doc(domain="test.com", content="Some content here.", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            total = sm.get_total_size()
            assert total > 0


class TestStorageManagerChunks:
    """Tests for save_chunks."""

    def test_save_chunks_updates_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            sm.save_doc(domain="test.com", content="Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            chunks = [
                ("/fake/path/doc_part_01.md", 1024),
                ("/fake/path/doc_part_02.md", 2048),
            ]
            sm.save_chunks("test.com", chunks)
            meta = sm.get_metadata("test.com")
            assert meta["chunks"] == 2
            assert len(meta["chunks_list"]) == 2
            assert meta["chunks_list"][0]["filename"] == "doc_part_01.md"
            assert meta["chunks_list"][0]["size"] == 1024


# ════════════════════════════════════════════════════════════════
#  VERSION MANAGER
# ════════════════════════════════════════════════════════════════

class TestVersionManagerInit:
    """Tests for VersionManager initialization."""

    def test_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            assert vm.storage is sm


class TestVersionManagerSnapshot:
    """Tests for snapshot creation."""

    def test_snapshot_creates_version_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="# V1 Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            version = vm.snapshot("test.com")
            assert version == "v1.0.1"  # bumped from 1.0.0
            vpath = sm.versions_dir("test.com") / "v1.0.1.md"
            assert vpath.exists()
            assert vpath.read_text(encoding="utf-8") == "# V1 Content"

    def test_snapshot_bumps_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            v1 = vm.snapshot("test.com")
            v2 = vm.snapshot("test.com")
            assert v1 == "v1.0.1"
            assert v2 == "v1.0.2"

    def test_snapshot_raises_without_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            with pytest.raises(VersioningError, match="No current docs"):
                vm.snapshot("nonexistent.com")

    def test_snapshot_updates_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            version = vm.snapshot("test.com")
            meta = sm.get_metadata("test.com")
            assert meta["latest_version"] == version
            version_names = [v["version"] for v in meta["versions"]]
            assert version in version_names

    def test_snapshot_marks_old_not_latest(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            vm.snapshot("test.com")  # v1.0.2
            meta = sm.get_metadata("test.com")
            latest_versions = [v for v in meta["versions"] if v["is_latest"]]
            assert len(latest_versions) == 1
            assert latest_versions[0]["version"] == "v1.0.2"


class TestVersionManagerQueries:
    """Tests for get_versions, get_version_content."""

    def test_get_versions_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            assert vm.get_versions("nonexistent.com") == []

    def test_get_versions_after_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")
            vm.snapshot("test.com")
            versions = vm.get_versions("test.com")
            assert len(versions) >= 1  # at least the initial 1.0.0 + snapshots

    def test_get_version_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Version content", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")
            content = vm.get_version_content("test.com", "v1.0.1")
            assert content == "Version content"

    def test_get_version_content_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            content = vm.get_version_content("test.com", "v99.99.99")
            assert content is None


class TestVersionManagerDiff:
    """Tests for diff."""

    def test_diff_between_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Line 1\nLine 2", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            # Modify content
            sm.latest_path("test.com").write_text("Line 1\nLine 3", encoding="utf-8")
            vm.snapshot("test.com")  # v1.0.2
            diff_text = vm.diff("test.com", "1.0.1", "1.0.2")
            assert "Line 2" in diff_text or "Line 3" in diff_text

    def test_diff_raises_on_missing_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            with pytest.raises(VersioningError, match="not found"):
                vm.diff("test.com", "1.0.0", "1.0.1")

    def test_diff_same_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Same", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            vm.snapshot("test.com")  # v1.0.2
            diff_text = vm.diff("test.com", "1.0.1", "1.0.2")
            # No diff lines (only header)
            assert diff_text.count("\n+") <= 0 or diff_text.count("\n-") <= 0


class TestVersionManagerRollback:
    """Tests for rollback."""

    def test_rollback_restores_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Version 1", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            # Update content
            sm.save_doc(domain="test.com", content="Version 2", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.2)
            vm.snapshot("test.com")  # v1.0.2
            # Rollback to v1.0.1
            result = vm.rollback("test.com", "1.0.1")
            assert result == "v1.0.1"
            content = sm.load_doc("test.com")
            assert "Version 1" in content

    def test_rollback_raises_on_missing_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            with pytest.raises(VersioningError, match="not found"):
                vm.rollback("test.com", "99.0.0")

    def test_rollback_snapshots_current_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="V1", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            sm.save_doc(domain="test.com", content="V2", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.2
            # Now rollback — should snapshot V2 before restoring V1
            vm.rollback("test.com", "1.0.1")
            # There should now be a v1.0.3 (the auto-snapshot)
            vpath = sm.versions_dir("test.com") / "v1.0.3.md"
            assert vpath.exists()


class TestVersionManagerChangelog:
    """Tests for changelog generation."""

    def test_changelog_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            entries = vm.changelog("nonexistent.com")
            assert entries == []

    def test_changelog_with_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            sm = StorageManager(base_dir=tmp)
            vm = VersionManager(sm)
            sm.save_doc(domain="test.com", content="Line 1\nLine 2", url="u",
                        title="T", pages=1, provider="generic", new_pages=1, size_kb=0.1)
            vm.snapshot("test.com")  # v1.0.1
            sm.latest_path("test.com").write_text("Line 1\nLine 3", encoding="utf-8")
            vm.snapshot("test.com")  # v1.0.2
            entries = vm.changelog("test.com")
            assert len(entries) >= 1
            assert "version" in entries[0]
            assert "added_lines" in entries[0]
            assert "removed_lines" in entries[0]
