"""Per-domain directory storage manager for gitbook-downloader v6.

Manages the on-disk layout under ~/.gitbook-downloader/docs/<domain>/,
including docs.md, metadata.json, version snapshots, and chunk metadata.
"""

import json
import os
import shutil
import time
from pathlib import Path


class StorageManager:
    """Manages per-domain directory storage for downloaded documentation.

    Layout::

        ~/.gitbook-downloader/
        └── docs/
            └── <domain>/
                ├── metadata.json      # Domain metadata
                ├── docs.md            # Latest full dump (all pages concatenated)
                ├── chunks/            # Optional chunk files
                │   ├── docs_part_01.md
                │   └── docs_part_02.md
                └── versions/          # Semver snapshots
                    ├── v1.0.0.md
                    └── v1.0.1.md
    """

    BASE_DIR = Path.home() / ".gitbook-downloader"

    def __init__(self, base_dir=None):
        """Initialize with optional custom base directory.

        Args:
            base_dir: Override the default base directory (``~/.gitbook-downloader``).
                      Strings are expanded and resolved; ``Path`` objects are accepted.
        """
        self.base = Path(base_dir).expanduser().resolve() if base_dir else self.BASE_DIR

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

    def versions_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/versions/``."""
        return self._domain_dir(domain) / "versions"

    def chunks_dir(self, domain: str) -> Path:
        """Return ``~/.gitbook-downloader/docs/<domain>/chunks/``."""
        return self._domain_dir(domain) / "chunks"

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------

    def ensure_domain_dir(self, domain: str) -> Path:
        """Create the domain directory tree if it doesn't exist.

        Returns the domain directory path.
        """
        ddir = self._domain_dir(domain)
        ddir.mkdir(parents=True, exist_ok=True)
        return ddir

    def domain_exists(self, domain: str) -> bool:
        """Check if a domain has been downloaded (docs.md present)."""
        return self.latest_path(domain).exists()

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def save_doc(
        self,
        domain: str,
        content: str,
        *,
        url=None,
        title=None,
        pages=1,
        provider="",
        new_pages=0,
        size_kb=0,
    ):
        """Save downloaded documentation content for a domain.

        Creates the domain directory if needed.  Writes ``docs.md`` and
        creates or updates ``metadata.json``.

        Args:
            domain: Domain name used as directory key.
            content: Full Markdown content to write.
            url: Source URL of the documentation.
            title: Human-readable title for the domain.
            pages: Total number of pages scraped.
            provider: Provider identifier (e.g. "gitbook", "readthedocs").
            new_pages: Number of newly scraped pages in this run.
            size_kb: Approximate size in kilobytes.

        Returns:
            dict: The domain metadata after saving.
        """
        self.ensure_domain_dir(domain)

        # Write content
        self.latest_path(domain).write_text(content, encoding="utf-8")

        # Update metadata
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
            meta["update_history"].insert(
                0,
                {
                    "date": now,
                    "new_pages": new_pages,
                    "total_pages": pages,
                    "size_kb": size_kb,
                },
            )
            # Trim history to last 50 entries
            meta["update_history"] = meta["update_history"][:50]

        self._write_metadata(domain, meta)
        return meta

    def load_doc(self, domain: str):
        """Read the latest ``docs.md`` for a domain.

        Args:
            domain: Domain name.

        Returns:
            str or None: File contents, or ``None`` if the file does not exist.
        """
        path = self.latest_path(domain)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def load_doc_version(self, domain: str, version: str):
        """Read a specific version's ``docs.md``.

        Args:
            domain: Domain name.
            version: Version string (with or without ``v`` prefix).

        Returns:
            str or None: File contents, or ``None`` if the version file does not exist.
        """
        vpath = self.versions_dir(domain) / f"v{version.lstrip('v')}.md"
        return vpath.read_text(encoding="utf-8") if vpath.exists() else None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self, domain: str):
        """Read ``metadata.json`` for a domain.

        Args:
            domain: Domain name.

        Returns:
            dict or None: Parsed metadata, or ``None`` if not found or corrupt.
        """
        path = self.metadata_path(domain)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _write_metadata(self, domain: str, metadata: dict):
        """Write ``metadata.json`` for a domain.

        Args:
            domain: Domain name.
            metadata: Metadata dictionary to serialize.
        """
        self.ensure_domain_dir(domain)
        path = self.metadata_path(domain)
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # Listing / Stats
    # ------------------------------------------------------------------

    def list_domains(self):
        """List all downloaded domains with their metadata.

        Returns:
            list[dict]: A list of metadata dictionaries, one per domain,
            sorted alphabetically by domain name.
        """
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
        """Total size of all downloaded docs in bytes.

        Returns:
            int: Sum of file sizes across all domains and sub-directories.
        """
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
        """Delete all data for a domain.

        Args:
            domain: Domain name.

        Returns:
            bool: ``True`` if the domain was deleted, ``False`` if it didn't exist.
        """
        ddir = self._domain_dir(domain)
        if ddir.exists():
            shutil.rmtree(ddir)
            return True
        return False

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------

    def save_chunks(self, domain: str, chunks: list):
        """Record chunk metadata in the domain directory.

        This stores the chunk manifest in ``metadata.json`` so that later
        consumers (search indexer, RAG pipeline, etc.) can discover chunk
        files without scanning the filesystem.

        Args:
            domain: Domain name.
            chunks: List of ``(filename, size_bytes)`` tuples.
        """
        self.ensure_domain_dir(domain)
        chunk_dir = self.chunks_dir(domain)
        chunk_dir.mkdir(parents=True, exist_ok=True)

        meta = self.get_metadata(domain) or {}
        meta["chunks"] = len(chunks)
        meta["chunks_list"] = [
            {"filename": os.path.basename(fn), "size": sz} for fn, sz in chunks
        ]
        self._write_metadata(domain, meta)
