"""Semver versioning manager for gitbook-downloader v7.

Provides snapshot, rollback, diff, and changelog operations over the
versioned ``docs.md`` copies stored in
``~/.gitbook-downloader/docs/<domain>/versions/``.

v7 hardening (plan §5):

- Snapshot files are written **atomically** (temp + rename).
- The next version number is derived from *both* the metadata registry and
  the files actually on disk, so a rebuilt/lost registry can never cause a
  snapshot to overwrite an existing version file.
- ``rollback`` never inflates the version history for the restore itself:
  it only takes a safety snapshot of the current state when that state
  actually differs from the target being restored.
"""

import difflib
import logging
import time

from .manager import (
    StorageManager,
    atomic_write_text,
    format_semver,
    parse_semver,
)

logger = logging.getLogger(__name__)


class VersioningError(Exception):
    """Raised when a versioning operation fails."""


class VersionManager:
    """Manages version snapshots of downloaded documentation.

    Each *snapshot* copies the current ``docs.md`` into the ``versions/``
    directory with a semver filename (``v<major>.<minor>.<patch>.md``).
    The patch number is auto-incremented on every snapshot.

    Args:
        storage: A :class:`~storage.manager.StorageManager` instance used
                 for all underlying file I/O.
    """

    def __init__(self, storage: StorageManager):
        self.storage = storage

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_versions_dir(self, domain: str):
        """Return the versions directory for *domain*."""
        return self.storage.versions_dir(domain)

    def _parse_version(self, version_str: str) -> tuple[int, int, int]:
        """Parse a version string into ``(major, minor, patch)``.

        Accepts ``"1.2.3"`` or ``"v1.2.3"``. Missing components default to 0;
        unparseable strings fall back to ``(0, 0, 0)``.
        """
        parts = parse_semver(version_str)
        if parts is None:
            tail = str(version_str).lstrip("v").split(".")
            nums = []
            for piece in tail[:3]:
                try:
                    nums.append(int(piece))
                except ValueError:
                    nums.append(0)
            while len(nums) < 3:
                nums.append(0)
            return (nums[0], nums[1], nums[2])
        return parts

    def _version_str(self, parts: tuple[int, int, int]) -> str:
        """Format a ``(major, minor, patch)`` tuple as ``"v<m>.<m>.<p>"``."""
        return format_semver(parts)

    def _next_version(self, current_version: str) -> str:
        """Bump the patch component: ``"1.0.0"`` → ``"v1.0.1"``."""
        parts = self._parse_version(current_version)
        return self._version_str((parts[0], parts[1], parts[2] + 1))

    def _highest_disk_version(self, domain: str) -> str | None:
        """Return the highest ``vX.Y.Z`` filename present on disk, or None."""
        vdir = self._get_versions_dir(domain)
        if not vdir.is_dir():
            return None
        best: tuple[int, int, int] | None = None
        for f in vdir.iterdir():
            if not f.is_file() or f.suffix != ".md":
                continue
            parts = parse_semver(f.stem)
            if parts is None:
                continue
            if best is None or parts > best:
                best = parts
        return format_semver(best) if best else None

    def _ensure_meta(self, domain: str) -> dict:
        """Return usable metadata for *domain*, creating a skeleton if needed."""
        meta = self.storage.get_metadata(domain)
        if meta is None:
            meta = {
                "domain": domain,
                "url": "",
                "title": domain,
                "provider": "",
                "first_scraped": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "last_scraped": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_pages": 0,
                "total_size_kb": 0,
                "latest_version": "1.0.0",
                "versions": [],
                "update_history": [],
            }
        meta.setdefault("versions", [])
        meta.setdefault("latest_version", "1.0.0")
        return meta

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self, domain: str) -> str:
        """Copy current ``docs.md`` into ``versions/v<next>.md``.

        The new version number bumps the patch component of the current
        ``latest_version``, and keeps bumping past any version file that
        already exists on disk (registry/disk desync protection).

        If the content is byte-identical to the latest existing version
        file, no new version file is created — the existing latest version
        id is returned, so re-captures of unchanged sites cannot inflate
        the version history. Content that differs (including rollback
        safety snapshots) always produces a new version.

        Args:
            domain: Domain name.

        Returns:
            str: The version string, e.g. ``"v1.0.1"`` — either the newly
            created version, or the existing latest one when unchanged.

        Raises:
            VersioningError: If no current docs exist for the domain.
        """
        content = self.storage.load_doc(domain)
        if content is None:
            raise VersioningError(f"No current docs found for {domain}")

        # Registry consistency first: adopt stray files / drop dangling
        # entries so the next-version computation sees reality.
        self.storage.reconcile_versions(domain)

        meta = self._ensure_meta(domain)
        candidates = [
            meta.get("latest_version", "1.0.0"),
            self._highest_disk_version(domain) or "0.0.0",
        ]
        newest = max(candidates, key=self._parse_version)

        vdir = self._get_versions_dir(domain)

        # Skip byte-identical re-snapshots: creating another copy of an
        # unchanged docs.md only inflates the versions/ directory.
        latest_file = vdir / f"v{str(newest).lstrip('v')}.md"
        if latest_file.is_file():
            try:
                unchanged = latest_file.read_bytes() == content.encode("utf-8")
            except OSError:
                unchanged = False
            if unchanged:
                latest_clean = f"v{str(newest).lstrip('v')}"
                logger.info(
                    "Content of %s is unchanged; keeping version %s (no new snapshot)",
                    domain,
                    latest_clean,
                )
                # The early return must not strand a stale registry pointer:
                # if the registry disagrees with the disk truth we just
                # verified, heal latest_version before returning.
                if meta.get("latest_version") != latest_clean:
                    for v in meta["versions"]:
                        v["is_latest"] = v.get("version") == latest_clean
                    meta["latest_version"] = latest_clean
                    self.storage._write_metadata(domain, meta)
                return latest_clean

        vdir.mkdir(parents=True, exist_ok=True)
        new_version = self._next_version(newest)
        vpath = vdir / f"{new_version}.md"
        while vpath.exists():  # paranoia: never overwrite a snapshot
            new_version = self._next_version(new_version)
            vpath = vdir / f"{new_version}.md"

        atomic_write_text(vpath, content)

        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        for v in meta["versions"]:
            v["is_latest"] = False
        meta["versions"].append({
            "version": new_version,
            "timestamp": now,
            "pages": meta.get("total_pages", 0),
            "size_kb": meta.get("total_size_kb", 0),
            "is_latest": True,
        })
        meta["latest_version"] = new_version
        self.storage._write_metadata(domain, meta)

        return new_version

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_versions(self, domain: str) -> list:
        """List all available versions for a domain (chronological order)."""
        meta = self.storage.get_metadata(domain)
        if not meta:
            return []
        return meta.get("versions", [])

    def get_version_content(self, domain: str, version: str):
        """Read a specific version's content, or ``None`` if it doesn't exist."""
        return self.storage.load_doc_version(domain, version)

    # ------------------------------------------------------------------
    # Diff
    # ------------------------------------------------------------------

    def diff(self, domain: str, v1: str, v2: str) -> str:
        """Generate a unified diff between two versions.

        Both versions must exist in the ``versions/`` directory.

        Raises:
            VersioningError: If either version is not found.
        """
        c1 = self.get_version_content(domain, v1)
        c2 = self.get_version_content(domain, v2)

        if c1 is None:
            raise VersioningError(f"Version {v1} not found for {domain}")
        if c2 is None:
            raise VersioningError(f"Version {v2} not found for {domain}")

        diff = difflib.unified_diff(
            c1.splitlines(),
            c2.splitlines(),
            fromfile=f"{domain} v{str(v1).lstrip('v')}",
            tofile=f"{domain} v{str(v2).lstrip('v')}",
            lineterm="",
            n=3,
        )
        return "\n".join(diff)

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def rollback(self, domain: str, version: str) -> str:
        """Restore a historical version as the current ``docs.md``.

        No version inflation: the restored state simply becomes
        ``latest_version`` again. A safety snapshot of the pre-rollback
        state is taken *only* when that state differs from the target
        content — rolling back to what is already live is a no-op for the
        version registry.

        Args:
            domain: Domain name.
            version: Version to restore (with or without ``v`` prefix).

        Returns:
            str: The restored version string (e.g. ``"v1.0.0"``).

        Raises:
            VersioningError: If the requested version does not exist.
        """
        content = self.get_version_content(domain, version)
        if content is None:
            raise VersioningError(f"Version {version} not found for {domain}")

        current = self.storage.load_doc(domain)
        if current is not None and current != content:
            # Safety snapshot of genuinely different current state.
            try:
                self.snapshot(domain)
            except VersioningError:
                pass  # No current content — fine for first rollback

        version_clean = str(version).lstrip("v")
        atomic_write_text(self.storage.latest_path(domain), content)

        meta = self.storage.get_metadata(domain)
        if meta:
            target_names = {f"v{version_clean}", version_clean}
            for v in meta.get("versions", []):
                v["is_latest"] = v.get("version") in target_names
            meta["latest_version"] = f"v{version_clean}"
            self.storage._write_metadata(domain, meta)

        return f"v{version_clean}"

    # ------------------------------------------------------------------
    # Changelog
    # ------------------------------------------------------------------

    def changelog(self, domain: str) -> list:
        """Auto-generate changelog entries from all version diffs.

        Iterates over consecutive version pairs (newest first) and counts
        added / removed lines.
        """
        versions = self.get_versions(domain)
        entries = []

        for i in range(len(versions) - 1, 0, -1):
            v_older = versions[i - 1]["version"].lstrip("v")
            v_newer = versions[i]["version"].lstrip("v")
            try:
                diff_text = self.diff(domain, v_older, v_newer)
            except VersioningError:
                continue
            added = sum(
                1
                for line in diff_text.split("\n")
                if line.startswith("+") and not line.startswith("+++")
            )
            removed = sum(
                1
                for line in diff_text.split("\n")
                if line.startswith("-") and not line.startswith("---")
            )
            entries.append(
                {
                    "version": f"v{v_newer}",
                    "timestamp": versions[i].get("timestamp", ""),
                    "added_lines": added,
                    "removed_lines": removed,
                    "diff": diff_text,
                }
            )

        return entries
