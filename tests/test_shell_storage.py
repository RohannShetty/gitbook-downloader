"""Shell-lane tests — storage hardening (plan §5).

Atomic writes, corrupt-metadata recovery, registry consistency, per-domain
lockfile, rollback without version inflation. All on temp dirs.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from gitbook_downloader.storage import (
    StorageManager,
    VersionManager,
    VersioningError,
)
from gitbook_downloader.storage.manager import (
    DomainLock,
    LockHeldError,
    atomic_write_text,
)


@pytest.fixture
def sm(tmp_path):
    return StorageManager(base_dir=tmp_path)


def seed_domain(sm: StorageManager, domain: str = "test.com",
                content: str = "Content") -> None:
    sm.save_doc(domain=domain, content=content, url="https://x.com/",
                title="T", pages=1, provider="generic", new_pages=1,
                size_kb=0.1)


# ── Atomic writes ───────────────────────────────────────────────────────


class TestAtomicWrite:
    def test_writes_content(self, tmp_path):
        dest = tmp_path / "sub" / "file.md"
        atomic_write_text(dest, "hello")
        assert dest.read_text(encoding="utf-8") == "hello"

    def test_no_tmp_files_left_behind(self, tmp_path):
        dest = tmp_path / "file.md"
        for i in range(5):
            atomic_write_text(dest, f"v{i}")
        leftovers = [p for p in tmp_path.iterdir() if p.name != "file.md"]
        assert leftovers == []

    def test_failed_write_leaves_destination_untouched(
            self, tmp_path, monkeypatch):
        dest = tmp_path / "file.md"
        atomic_write_text(dest, "original")

        real_replace = os.replace

        def broken_replace(src, dst):
            raise OSError("disk on fire")

        monkeypatch.setattr(os, "replace", broken_replace)
        with pytest.raises(OSError):
            atomic_write_text(dest, "corrupted")
        monkeypatch.setattr(os, "replace", real_replace)

        assert dest.read_text(encoding="utf-8") == "original"
        leftovers = [p for p in tmp_path.iterdir() if p.name != "file.md"]
        assert leftovers == []  # temp file cleaned up

    def test_metadata_and_docs_written_atomically(self, sm):
        seed_domain(sm)
        # No stray temp files anywhere in the domain dir.
        strays = [p for p in sm._domain_dir("test.com").rglob("*")
                  if p.is_file() and ".tmp" in p.name]
        assert strays == []


# ── Corrupt metadata recovery ───────────────────────────────────────────


class TestCorruptMetadataRecovery:
    def test_corrupt_metadata_rebuilt_from_version_files(self, sm):
        seed_domain(sm, content="V1")
        vm = VersionManager(sm)
        vm.snapshot("test.com")                       # v1.0.1
        sm.latest_path("test.com").write_text("V2", encoding="utf-8")
        vm.snapshot("test.com")                       # v1.0.2

        # Corrupt the registry.
        sm.metadata_path("test.com").write_text("{not json!!", encoding="utf-8")

        meta = sm.get_metadata("test.com")
        assert meta is not None
        # NEVER reset to 1.0.0 when history exists on disk.
        assert meta["latest_version"] == "v1.0.2"
        versions = {v["version"] for v in meta["versions"]}
        assert {"v1.0.1", "v1.0.2"} <= versions
        assert meta["rebuilt_from_disk"] is True

    def test_rebuild_persists_self_healed_metadata(self, sm):
        seed_domain(sm)
        VersionManager(sm).snapshot("test.com")
        sm.metadata_path("test.com").write_text("garbage", encoding="utf-8")

        meta = sm.get_metadata("test.com")
        # Self-healed: readable again from disk.
        healed = json.loads(
            sm.metadata_path("test.com").read_text(encoding="utf-8"))
        assert healed["latest_version"] == meta["latest_version"]

    def test_truncated_json_counts_as_corrupt(self, sm):
        seed_domain(sm)
        VersionManager(sm).snapshot("test.com")
        raw = sm.metadata_path("test.com").read_text(encoding="utf-8")
        sm.metadata_path("test.com").write_text(raw[: len(raw) // 2],
                                                encoding="utf-8")
        meta = sm.get_metadata("test.com")
        assert meta["latest_version"] == "v1.0.1"

    def test_missing_metadata_with_history_on_disk_is_rebuilt(self, sm):
        seed_domain(sm)
        VersionManager(sm).snapshot("test.com")
        os.unlink(sm.metadata_path("test.com"))

        meta = sm.rebuild_metadata("test.com")
        assert meta["latest_version"] == "v1.0.1"

    def test_unknown_domain_still_returns_none(self, sm):
        assert sm.get_metadata("ghost.com") is None
        assert sm.rebuild_metadata("ghost.com") is None

    def test_save_doc_preserves_latest_version_after_rebuild(self, sm):
        seed_domain(sm)
        vm = VersionManager(sm)
        vm.snapshot("test.com")
        vm.snapshot("test.com")  # v1.0.2
        sm.metadata_path("test.com").write_text("###", encoding="utf-8")

        sm.save_doc(domain="test.com", content="New", url="u", title="T",
                    pages=2, provider="generic", new_pages=2, size_kb=0.2)
        meta = sm.get_metadata("test.com")
        assert meta["latest_version"] != "1.0.0"
        assert meta["latest_version"].startswith("v1.0.2")


# ── Registry consistency ────────────────────────────────────────────────


class TestReconcileVersions:
    def test_adopts_stray_version_files(self, sm):
        seed_domain(sm)
        vdir = sm.versions_dir("test.com")
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / "v1.0.9.md").write_text("stray", encoding="utf-8")

        report = sm.reconcile_versions("test.com")
        assert "v1.0.9" in report["adopted"]
        meta = sm.get_metadata("test.com")
        assert any(v["version"] == "v1.0.9" for v in meta["versions"])
        assert meta["latest_version"] == "v1.0.9"  # highest wins

    def test_drops_dangling_entries(self, sm):
        seed_domain(sm)
        vm = VersionManager(sm)
        vm.snapshot("test.com")  # v1.0.1
        os.unlink(sm.versions_dir("test.com") / "v1.0.1.md")

        report = sm.reconcile_versions("test.com")
        assert "v1.0.1" in report["dropped"]
        meta = sm.get_metadata("test.com")
        assert all(v["version"] != "v1.0.1" for v in meta["versions"])

    def test_exactly_one_latest_after_reconcile(self, sm):
        seed_domain(sm)
        vm = VersionManager(sm)
        vm.snapshot("test.com")
        meta = sm.get_metadata("test.com")
        for v in meta["versions"]:
            v["is_latest"] = True  # corrupt the flags
        sm._write_metadata("test.com", meta)

        sm.reconcile_versions("test.com")
        meta = sm.get_metadata("test.com")
        latest = [v for v in meta["versions"] if v["is_latest"]]
        assert len(latest) == 1
        assert latest[0]["version"] == meta["latest_version"]

    def test_snapshot_after_manual_file_loss_never_overwrites(
            self, sm):
        seed_domain(sm)
        vm = VersionManager(sm)
        vm.snapshot("test.com")  # v1.0.1
        # Simulate a lost registry pointing at an old version while disk
        # already has v1.0.1.
        meta = sm.get_metadata("test.com")
        meta["latest_version"] = "1.0.0"
        sm._write_metadata("test.com", meta)

        version = vm.snapshot("test.com")
        assert version == "v1.0.2"  # bumped past the existing file
        assert (sm.versions_dir("test.com") / "v1.0.1.md").exists()


# ── Per-domain lockfile ─────────────────────────────────────────────────


class TestDomainLock:
    def test_acquire_and_release(self, sm):
        lock = sm.domain_lock("test.com")
        with lock as acquired:
            assert acquired.path.exists()
        assert not acquired.path.exists()

    def test_second_lock_raises(self, sm):
        with sm.domain_lock("test.com"):
            with pytest.raises(LockHeldError, match="test.com"):
                sm.domain_lock("test.com").acquire()

    def test_stale_lock_is_stolen(self, sm):
        stale = sm.domain_lock("test.com")
        stale.acquire()
        # Backdate the lock file so it looks abandoned (default threshold
        # is 15 minutes).
        past = time.time() - 3600
        os.utime(stale.path, (past, past))

        fresh = sm.domain_lock("test.com")
        fresh.acquire()  # must not raise
        try:
            assert fresh.path.exists()
        finally:
            fresh.release()

    def test_release_idempotent(self, sm):
        lock = sm.domain_lock("test.com")
        lock.acquire()
        lock.release()
        lock.release()  # no error

    def test_lock_records_pid(self, sm):
        with sm.domain_lock("test.com") as lock:
            payload = lock.path.read_text(encoding="utf-8")
            assert f"pid={os.getpid()}" in payload


# ── Rollback without version inflation ──────────────────────────────────


class TestRollbackNoInflation:
    def test_rollback_to_same_content_creates_no_new_version(self, sm):
        seed_domain(sm, content="Same")
        vm = VersionManager(sm)
        vm.snapshot("test.com")            # v1.0.1 ("Same")
        before = set(p.name for p in
                     sm.versions_dir("test.com").iterdir())

        result = vm.rollback("test.com", "1.0.1")
        assert result == "v1.0.1"

        after = set(p.name for p in sm.versions_dir("test.com").iterdir())
        assert after == before  # no inflation
        meta = sm.get_metadata("test.com")
        assert meta["latest_version"] == "v1.0.1"

    def test_rollback_to_different_content_takes_one_safety_snapshot(
            self, sm):
        seed_domain(sm, content="V1")
        vm = VersionManager(sm)
        vm.snapshot("test.com")                        # v1.0.1
        sm.latest_path("test.com").write_text("V2", encoding="utf-8")
        vm.snapshot("test.com")                        # v1.0.2

        vm.rollback("test.com", "1.0.1")
        files = sorted(p.name for p in
                       sm.versions_dir("test.com").iterdir())
        assert files == ["v1.0.1.md", "v1.0.2.md", "v1.0.3.md"]
        # Exactly ONE safety snapshot, and repeated rollbacks don't add more.
        vm.rollback("test.com", "1.0.1")
        files_again = sorted(p.name for p in
                             sm.versions_dir("test.com").iterdir())
        assert files_again == files

    def test_rollback_updates_latest_pointer(self, sm):
        seed_domain(sm, content="V1")
        vm = VersionManager(sm)
        vm.snapshot("test.com")
        sm.latest_path("test.com").write_text("V2", encoding="utf-8")
        vm.snapshot("test.com")
        vm.rollback("test.com", "1.0.1")

        meta = sm.get_metadata("test.com")
        assert meta["latest_version"] == "v1.0.1"
        assert sm.load_doc("test.com") == "V1"

    def test_rollback_missing_version_raises(self, sm):
        seed_domain(sm)
        with pytest.raises(VersioningError, match="not found"):
            VersionManager(sm).rollback("test.com", "99.0.0")


# ── Base-dir env override ───────────────────────────────────────────────


class TestBaseDirEnvOverride:
    def test_env_var_overrides_default_base(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path))
        manager = StorageManager()
        assert manager.base == tmp_path.resolve()

    def test_explicit_base_beats_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME",
                           str(tmp_path / "env"))
        manager = StorageManager(base_dir=tmp_path / "explicit")
        assert manager.base == (tmp_path / "explicit").resolve()

    def test_no_env_falls_back_to_home(self, monkeypatch):
        monkeypatch.delenv("GITBOOK_DOWNLOADER_HOME", raising=False)
        manager = StorageManager()
        assert manager.base == Path.home() / ".gitbook-downloader"
