"""Semver versioning manager for gitbook-downloader v6.

Provides snapshot, rollback, diff, and changelog operations over the
versioned ``docs.md`` copies stored in ``~/.gitbook-downloader/docs/<domain>/versions/``.
"""

import difflib
import time
from pathlib import Path


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

    def __init__(self, storage):
        self.storage = storage

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_versions_dir(self, domain: str) -> Path:
        """Return the versions directory for *domain*."""
        return self.storage.versions_dir(domain)

    def _parse_version(self, version_str: str) -> tuple:
        """Parse a version string into ``(major, minor, patch)``.

        Accepts ``"1.2.3"`` or ``"v1.2.3"``.  Missing components default
        to ``0``.

        Returns:
            tuple[int, int, int]
        """
        parts = version_str.lstrip("v").split(".")
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)

    def _version_str(self, parts: tuple) -> str:
        """Format a ``(major, minor, patch)`` tuple as ``"v<m>.<m>.<p>"``."""
        return f"v{parts[0]}.{parts[1]}.{parts[2]}"

    def _next_version(self, current_version: str) -> str:
        """Bump the patch component: ``"1.0.0"`` → ``"v1.0.1"``."""
        parts = self._parse_version(current_version)
        return self._version_str((parts[0], parts[1], parts[2] + 1))

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self, domain: str) -> str:
        """Copy current ``docs.md`` into ``versions/v<next>.md``.

        The new version number is the current ``latest_version`` from
        metadata with the patch component incremented by 1.

        Args:
            domain: Domain name.

        Returns:
            str: The new version string, e.g. ``"v1.0.1"``.

        Raises:
            VersioningError: If no current docs exist for the domain.
        """
        content = self.storage.load_doc(domain)
        if content is None:
            raise VersioningError(f"No current docs found for {domain}")

        meta = self.storage.get_metadata(domain)
        current_ver = meta.get("latest_version", "1.0.0") if meta else "1.0.0"
        new_version = self._next_version(current_ver)

        # Write version file
        vdir = self._get_versions_dir(domain)
        vdir.mkdir(parents=True, exist_ok=True)
        vpath = vdir / f"{new_version}.md"
        vpath.write_text(content, encoding="utf-8")

        # Mark old versions as not latest
        if meta and "versions" in meta:
            for v in meta["versions"]:
                v["is_latest"] = False

        # Update metadata
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        version_entry = {
            "version": new_version,
            "timestamp": now,
            "pages": meta.get("total_pages", 0) if meta else 0,
            "size_kb": meta.get("total_size_kb", 0) if meta else 0,
            "is_latest": True,
        }

        if meta:
            meta.setdefault("versions", []).append(version_entry)
            meta["latest_version"] = new_version
            self.storage._write_metadata(domain, meta)

        return new_version

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_versions(self, domain: str) -> list:
        """List all available versions for a domain.

        Args:
            domain: Domain name.

        Returns:
            list[dict]: Version entries from ``metadata.json``, ordered as
            stored (append order = chronological).
        """
        meta = self.storage.get_metadata(domain)
        if not meta:
            return []
        return meta.get("versions", [])

    def get_version_content(self, domain: str, version: str):
        """Read a specific version's content.

        Args:
            domain: Domain name.
            version: Version string (with or without ``v`` prefix).

        Returns:
            str or None: File contents, or ``None`` if the version doesn't exist.
        """
        return self.storage.load_doc_version(domain, version)

    # ------------------------------------------------------------------
    # Diff
    # ------------------------------------------------------------------

    def diff(self, domain: str, v1: str, v2: str) -> str:
        """Generate a unified diff between two versions.

        Uses ``difflib.unified_diff`` with 3 lines of context.  Both
        versions must exist in the ``versions/`` directory.

        Args:
            domain: Domain name.
            v1: First (older) version string.
            v2: Second (newer) version string.

        Returns:
            str: Unified diff text.

        Raises:
            VersioningError: If either version is not found.
        """
        c1 = self.get_version_content(domain, v1)
        c2 = self.get_version_content(domain, v2)

        if c1 is None:
            raise VersioningError(f"Version {v1} not found for {domain}")
        if c2 is None:
            raise VersioningError(f"Version {v2} not found for {domain}")

        lines1 = c1.splitlines()
        lines2 = c2.splitlines()

        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile=f"{domain} v{v1}",
            tofile=f"{domain} v{v2}",
            lineterm="",
            n=3,
        )
        return "\n".join(diff)

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def rollback(self, domain: str, version: str) -> str:
        """Restore a historical version as the current ``docs.md``.

        Before overwriting, the current ``docs.md`` is snapshotted so no
        data is lost.

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

        # Snapshot current before rollback
        try:
            self.snapshot(domain)
        except VersioningError:
            pass  # No current content — fine for first rollback

        # Write requested version as the latest
        version_clean = version.lstrip("v")
        latest_path = self.storage.latest_path(domain)
        latest_path.write_text(content, encoding="utf-8")

        # Update metadata
        meta = self.storage.get_metadata(domain)
        if meta:
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            for v in meta.get("versions", []):
                v["is_latest"] = v["version"] in (f"v{version_clean}", version_clean)
            meta["latest_version"] = f"v{version_clean}"
            self.storage._write_metadata(domain, meta)

        return f"v{version_clean}"

    # ------------------------------------------------------------------
    # Changelog
    # ------------------------------------------------------------------

    def changelog(self, domain: str) -> list:
        """Auto-generate changelog entries from all version diffs.

        Iterates over consecutive version pairs (newest first) and
        counts added / removed lines.

        Args:
            domain: Domain name.

        Returns:
            list[dict]: Entries with keys ``version``, ``timestamp``,
            ``added_lines``, ``removed_lines``, and ``diff``.
        """
        versions = self.get_versions(domain)
        entries = []

        for i in range(len(versions) - 1, 0, -1):
            v_older = versions[i - 1]["version"].lstrip("v")
            v_newer = versions[i]["version"].lstrip("v")
            try:
                diff_text = self.diff(domain, v_older, v_newer)
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
            except VersioningError:
                continue

        return entries
