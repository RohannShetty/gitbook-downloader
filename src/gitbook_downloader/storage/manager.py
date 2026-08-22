"""Per-domain directory storage manager for gitbook-downloader v7.

Manages the on-disk layout under ``~/.gitbook-downloader/docs/<domain>/``:

    ~/.gitbook-downloader/
    └── docs/
        └── <domain>/
            ├── metadata.json      # Domain metadata + versions[] registry
            ├── docs.md            # Latest full dump (book content)
            ├── llms.txt           # Manifest copy
            ├── pages/             # Page tree (per-page .md files)
            ├── chunks/            # Optional chunk files
            └── versions/          # Semver snapshots (v<major>.<minor>.<patch>.md)

v7 hardening (plan §5):

- **Atomic writes** — every file write goes through :func:`atomic_write_text`
  (temp file in the same directory + ``os.replace``), so a crash can never
  leave a half-written ``metadata.json`` or snapshot behind.
- **Corrupt metadata recovery** — if ``metadata.json`` is unreadable, it is
  rebuilt from the artifacts actually on disk (``versions/*.md``, ``docs.md``).
  ``latest_version`` is derived from the highest version file present and is
  NEVER silently reset to ``1.0.0`` when history exists.
- **Registry consistency** — :meth:`StorageManager.reconcile_versions` syncs
  the ``versions[]`` registry with the files on disk (adopts stray files,
  drops dangling entries) so ``history``/``diff`` never lie.
- **Per-domain lockfile** — :class:`DomainLock` serialises concurrent runs
  against the same domain.
"""

import json
import os
import re
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

# Environment variable overriding the library base directory (used by tests
# and sandboxed installs). Evaluated per-instance, not at import time.
ENV_BASE_DIR = "GITBOOK_DOWNLOADER_HOME"

# A lock older than this is considered abandoned and may be stolen.
LOCK_STALE_SECONDS = 15 * 60

_VERSION_FILE_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)\.md$")


def atomic_write_text(path: str | Path, text: str) -> Path:
    """Write *text* to *path* atomically (temp file + ``os.replace``).

    The temp file is created in the destination's own directory so the final
    rename stays on one filesystem. On any failure the temp file is removed
    and the destination is left untouched.

    Args:
        path: Destination file path.
        text: Text to write (UTF-8, LF line endings).

    Returns:
        The destination path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, str(path))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return path


def parse_semver(version_str: str) -> tuple[int, int, int] | None:
    """Parse ``"v1.2.3"`` / ``"1.2.3"`` into ``(major, minor, patch)``.

    Returns ``None`` when the string is not a plain three-part semver.
    """
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", str(version_str).strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def format_semver(parts: tuple[int, int, int]) -> str:
    """Format ``(major, minor, patch)`` as ``"v<major>.<minor>.<patch>"``."""
    return f"v{parts[0]}.{parts[1]}.{parts[2]}"


class LockHeldError(RuntimeError):
    """Raised when another process holds the per-domain lock."""


class DomainLock:
    """Filesystem lockfile serialising captures for one domain.

    The lock file lives at ``<base>/locks/<domain>.lock`` and is created with
    ``O_CREAT | O_EXCL`` (atomic on Windows and POSIX). Locks older than
    :data:`LOCK_STALE_SECONDS` are considered abandoned and stolen.
    """

    def __init__(self, base_dir: str | Path, domain: str,
                 stale_seconds: float = LOCK_STALE_SECONDS):
        self.base = Path(base_dir)
        self.domain = domain
        self.stale_seconds = stale_seconds
        self.path = self.base / "locks" / f"{domain}.lock"
        self._acquired = False

    def acquire(self) -> "DomainLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = f"pid={os.getpid()} at={time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                if self._is_stale():
                    # Steal the abandoned lock and retry once.
                    try:
                        self.path.unlink()
                    except OSError:
                        pass
                    continue
                raise LockHeldError(
                    f"Another gitbook-dl run appears to be capturing "
                    f"'{self.domain}' (lock: {self.path}). "
                    f"If this is wrong, delete the lock file."
                ) from None
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(payload)
                self._acquired = True
                return self

    def _is_stale(self) -> bool:
        try:
            age = time.time() - self.path.stat().st_mtime
        except OSError:
            return True
        return age > self.stale_seconds

    def release(self) -> None:
        if not self._acquired:
            return
        try:
            self.path.unlink()
        except OSError:
            pass
        self._acquired = False

    def __enter__(self) -> "DomainLock":
        return self.acquire()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


class StorageManager:
    """Manages per-domain directory storage for downloaded documentation."""

    BASE_DIR = Path.home() / ".gitbook-downloader"

    def __init__(self, base_dir=None):
        """Initialize with optional custom base directory.

        Args:
            base_dir: Override the default base directory
                      (``~/.gitbook-downloader``). When omitted, the
                      ``GITBOOK_DOWNLOADER_HOME`` environment variable is
                      honoured if set, otherwise the default is used.
        """
        if base_dir is not None:
            self.base = Path(base_dir).expanduser().resolve()
        else:
            env = os.environ.get(ENV_BASE_DIR)
            self.base = Path(env).expanduser().resolve() if env else self.BASE_DIR

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _domain_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/``."""
        return self.base / "docs" / domain

    def metadata_path(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/metadata.json``."""
        return self._domain_dir(domain) / "metadata.json"

    def latest_path(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/docs.md``."""
        return self._domain_dir(domain) / "docs.md"

    def manifest_path(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/llms.txt``."""
        return self._domain_dir(domain) / "llms.txt"

    def pages_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/pages/``."""
        return self._domain_dir(domain) / "pages"

    def versions_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/versions/``."""
        return self._domain_dir(domain) / "versions"

    def chunks_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/chunks/``."""
        return self._domain_dir(domain) / "chunks"

    def locks_dir(self) -> Path:
        """Return ``~/.gitbook-downloader/locks/``."""
        return self.base / "locks"

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------

    def ensure_domain_dir(self, domain: str) -> Path:
        """Create the domain directory tree if it doesn't exist."""
        ddir = self._domain_dir(domain)
        ddir.mkdir(parents=True, exist_ok=True)
        return ddir

    def domain_exists(self, domain: str) -> bool:
        """Check if a domain has been downloaded (docs.md present)."""
        return self.latest_path(domain).exists()

    def domain_lock(self, domain: str,
                    stale_seconds: float = LOCK_STALE_SECONDS) -> DomainLock:
        """Return an un-acquired :class:`DomainLock` for *domain*."""
        return DomainLock(self.base, domain, stale_seconds=stale_seconds)

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def save_doc(
        self,
        domain: str,
        content: str,
        *,
        url: str | None = None,
        title: str | None = None,
        pages: int = 1,
        provider: str = "",
        new_pages: int = 0,
        size_kb: float = 0.0,
    ):
        """Save downloaded documentation content for a domain.

        Creates the domain directory if needed. Writes ``docs.md``
        atomically and creates or updates ``metadata.json``. An existing
        ``latest_version`` / ``versions[]`` history is always preserved —
        snapshots are owned by :class:`~storage.versioning.VersionManager`.
        """
        self.ensure_domain_dir(domain)

        atomic_write_text(self.latest_path(domain), content)

        meta = self.get_metadata(domain)
        now = time.strftime("%Y-%m-%dT%H:%M:%S")

        if not meta:
            meta = {
                "domain": domain,
                "url": url or "",
                "title": title or domain,
                "provider": provider,
                "first_scraped": now,
                "last_scraped": now,
                "total_pages": pages,
                "total_size_kb": size_kb,
                "latest_version": "1.0.0",
                "versions": [
                    {
                        "version": "1.0.0",
                        "timestamp": now,
                        "pages": pages,
                        "size_kb": size_kb,
                        "is_latest": True,
                    }
                ],
                "update_history": [
                    {
                        "date": now,
                        "new_pages": new_pages,
                        "total_pages": pages,
                        "size_kb": size_kb,
                    }
                ],
            }
        else:
            meta["last_scraped"] = now
            meta["total_pages"] = pages
            meta["total_size_kb"] = size_kb
            meta.setdefault("update_history", []).insert(
                0,
                {
                    "date": now,
                    "new_pages": new_pages,
                    "total_pages": pages,
                    "size_kb": size_kb,
                },
            )
            meta["update_history"] = meta["update_history"][:50]
            if url:
                meta.setdefault("url", url)
            if provider:
                meta.setdefault("provider", provider)

        self._write_metadata(domain, meta)
        return meta

    def load_doc(self, domain: str):
        """Read the latest ``docs.md`` for a domain.

        Returns ``None`` if the file does not exist.
        """
        path = self.latest_path(domain)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def load_doc_version(self, domain: str, version: str):
        """Read a specific version's ``docs.md``.

        Accepts version strings with or without the ``v`` prefix.
        """
        vpath = self.versions_dir(domain) / f"v{str(version).lstrip('v')}.md"
        return vpath.read_text(encoding="utf-8") if vpath.exists() else None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self, domain: str):
        """Read ``metadata.json`` for a domain.

        If the file is corrupt (truncated, invalid JSON, unreadable), the
        metadata is rebuilt from the artifacts on disk via
        :meth:`rebuild_metadata` instead of being treated as absent —
        version history is never lost to a bad write.
        """
        path = self.metadata_path(domain)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            return self.rebuild_metadata(domain)

    def rebuild_metadata(self, domain: str):
        """Rebuild ``metadata.json`` from on-disk artifacts after corruption.

        Strategy:

        1. Every ``versions/vX.Y.Z.md`` file becomes a registry entry
           (timestamp from file mtime, size from file size).
        2. ``latest_version`` = highest version file found — NEVER reset to
           ``1.0.0`` when version history exists on disk.
        3. With no version files but a live ``docs.md``, a minimal fresh
           registry seeded at ``1.0.0`` is created (there is nothing older
           to preserve).
        4. With no artifacts at all, returns ``None`` (unknown domain).

        The rebuilt metadata is written back atomically (self-healing).
        """
        ddir = self._domain_dir(domain)
        if not ddir.exists():
            return None

        version_entries = []
        vdir = ddir / "versions"
        if vdir.is_dir():
            for f in sorted(vdir.iterdir()):
                parts = parse_semver(f.stem) if f.suffix == ".md" else None
                if parts is None or not f.is_file():
                    continue
                try:
                    stat = f.stat()
                except OSError:
                    continue
                version_entries.append({
                    "version": format_semver(parts),
                    "timestamp": time.strftime(
                        "%Y-%m-%dT%H:%M:%S", time.localtime(stat.st_mtime)
                    ),
                    "pages": 0,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "is_latest": False,
                    "rebuilt": True,
                })

        has_docs_md = (ddir / "docs.md").exists()
        if not version_entries and not has_docs_md:
            return None

        def _entry_key(e: dict) -> tuple[int, int, int]:
            parts = parse_semver(e["version"])
            return parts if parts is not None else (0, 0, 0)

        version_entries.sort(key=_entry_key)
        if version_entries:
            latest = version_entries[-1]["version"]
            version_entries[-1]["is_latest"] = True
        else:
            latest = "1.0.0"
            version_entries.append({
                "version": "1.0.0",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "pages": 0,
                "size_kb": 0,
                "is_latest": True,
                "rebuilt": True,
            })

        try:
            total_size_kb = round((ddir / "docs.md").stat().st_size / 1024, 1) \
                if has_docs_md else 0
        except OSError:
            total_size_kb = 0

        meta = {
            "domain": domain,
            "url": "",
            "title": domain,
            "provider": "",
            "first_scraped": version_entries[0]["timestamp"],
            "last_scraped": version_entries[-1]["timestamp"],
            "total_pages": 0,
            "total_size_kb": total_size_kb,
            "latest_version": latest,
            "versions": version_entries,
            "update_history": [],
            "rebuilt_from_disk": True,
        }
        self._write_metadata(domain, meta)
        return meta

    def reconcile_versions(self, domain: str) -> dict:
        """Sync the ``versions[]`` registry with the files on disk.

        - Adopts stray ``versions/vX.Y.Z.md`` files missing from the registry.
        - Drops registry entries whose version file vanished (except a lone
          fileless ``1.0.0`` seed entry, which represents the first capture).
        - Ensures exactly one ``is_latest`` entry and that ``latest_version``
          matches the highest known version.

        Returns:
            dict: ``{"adopted": [...], "dropped": [...], "latest": str}``.
        """
        meta = self.get_metadata(domain)
        if meta is None:
            return {"adopted": [], "dropped": [], "latest": ""}

        vdir = self.versions_dir(domain)
        disk_versions: dict[str, Path] = {}
        if vdir.is_dir():
            for f in vdir.iterdir():
                parts = parse_semver(f.stem) if f.suffix == ".md" else None
                if parts is not None and f.is_file():
                    disk_versions[format_semver(parts)] = f

        entries = list(meta.get("versions", []))
        known = {e.get("version") for e in entries}
        adopted, dropped = [], []

        # Adopt stray files.
        for ver, f in sorted(disk_versions.items()):
            if ver in known:
                continue
            try:
                stat = f.stat()
                size_kb = round(stat.st_size / 1024, 1)
                ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stat.st_mtime))
            except OSError:
                continue
            entries.append({
                "version": ver, "timestamp": ts, "pages": 0,
                "size_kb": size_kb, "is_latest": False, "adopted": True,
            })
            adopted.append(ver)

        # Drop dangling entries (registry says the file exists, disk disagrees).
        kept = []
        for e in entries:
            ver = e.get("version")
            if ver in disk_versions or (not disk_versions and len(entries) == 1):
                kept.append(e)
            else:
                dropped.append(ver)
        entries = kept

        if not entries:
            entries.append({
                "version": "1.0.0", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "pages": meta.get("total_pages", 0),
                "size_kb": meta.get("total_size_kb", 0), "is_latest": True,
            })

        def _entry_key(e: dict) -> tuple[int, int, int]:
            parts = parse_semver(e.get("version", ""))
            return parts if parts is not None else (0, 0, 0)

        entries.sort(key=_entry_key)
        for e in entries:
            e["is_latest"] = False
        entries[-1]["is_latest"] = True
        latest = entries[-1]["version"]

        meta["versions"] = entries
        meta["latest_version"] = latest
        self._write_metadata(domain, meta)
        return {"adopted": adopted, "dropped": dropped, "latest": latest}

    def _write_metadata(self, domain: str, metadata: dict):
        """Atomically write ``metadata.json`` for a domain."""
        self.ensure_domain_dir(domain)
        atomic_write_text(
            self.metadata_path(domain), json.dumps(metadata, indent=2)
        )

    # ------------------------------------------------------------------
    # Listing / Stats
    # ------------------------------------------------------------------

    def list_domains(self):
        """List all downloaded domains with their metadata (sorted by name)."""
        docs_dir = self.base / "docs"
        if not docs_dir.exists():
            return []
        domains = []
        for d in sorted(docs_dir.iterdir()):
            if d.is_dir():
                meta = self.get_metadata(d.name)
                if meta:
                    domains.append(meta)
        return domains

    def get_total_size(self) -> int:
        """Total size of all downloaded docs in bytes."""
        total = 0
        docs_dir = self.base / "docs"
        if docs_dir.exists():
            for f in docs_dir.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
        return total

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete_domain(self, domain: str) -> bool:
        """Delete all data for a domain. Returns True if it existed."""
        ddir = self._domain_dir(domain)
        if ddir.exists():
            shutil.rmtree(ddir)
            return True
        return False

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------

    def save_chunks(self, domain: str, chunks: list):
        """Record chunk metadata in the domain directory."""
        self.ensure_domain_dir(domain)
        self.chunks_dir(domain).mkdir(parents=True, exist_ok=True)

        meta = self.get_metadata(domain) or {}
        meta["chunks"] = len(chunks)
        meta["chunks_list"] = [
            {"filename": os.path.basename(fn), "size": sz} for fn, sz in chunks
        ]
        self._write_metadata(domain, meta)
