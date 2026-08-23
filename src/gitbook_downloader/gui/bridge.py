"""Python <-> JavaScript bridge for the Desktop GUI."""

from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from ..api import (
    CaptureOptions,
    ProgressEvent,
    capture,
    detect_site_versions,
)
from ..providers import detect_provider
from ..search.index import SearchIndex
from ..storage import StorageManager



class ApiBridge:
    """Methods exposed to the WebView JavaScript environment."""

    def __init__(self, window=None) -> None:
        self._window = window
        self._storage = StorageManager()
        self._cancel_requested = False
        self._active_thread: threading.Thread | None = None
        self._last_run: dict[str, Any] | None = None

    def set_window(self, window) -> None:
        self._window = window

    def _emit_to_js(self, func_name: str, data: Any) -> None:
        if self._window is None:
            return
        payload = json.dumps(data)
        js_code = f"if (window.{func_name}) {{ window.{func_name}({payload}); }}"
        try:
            self._window.evaluate_js(js_code)
        except Exception:
            pass

    # ── Detection ────────────────────────────────────────────────────────

    def detect(self, url: str) -> dict[str, Any]:
        """Detect the documentation provider and site versions for *url*."""
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            return {"success": False, "error": "Enter a valid http(s) URL"}
        try:
            sess = requests.Session()
            sess.headers["User-Agent"] = "gitbook-downloader/7.0.1"
            p = detect_provider(url, sess)
            provider_name = getattr(p, "name", "generic")
            evidence = getattr(p, "evidence", "") or f"Matched {provider_name} rules"
            
            site_versions = ()
            try:
                if hasattr(p, "discover_urls"):
                    urls = p.discover_urls(url)
                    if urls:
                        site_versions = detect_site_versions(urls)
            except Exception:
                pass

            return {
                "success": True,
                "url": url,
                "provider": provider_name,
                "evidence": evidence,
                "site_versions": list(site_versions),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ── Capture Execution ────────────────────────────────────────────────

    def start_capture(self, url: str, options: dict[str, Any]) -> dict[str, Any]:
        """Launch a capture job in a dedicated background worker thread."""
        if self._active_thread and self._active_thread.is_alive():
            return {"success": False, "error": "A capture is already running"}

        self._cancel_requested = False
        parsed_scope = tuple(
            s.strip() for s in options.get("path_scope", "").split(",") if s.strip()
        )
        parsed_exclude = tuple(
            s.strip() for s in options.get("exclude_paths", "").split(",") if s.strip()
        )
        site_versions = options.get("site_versions")
        if isinstance(site_versions, list):
            site_versions = tuple(site_versions) if site_versions else None
        else:
            site_versions = None

        max_pages = options.get("max_pages")
        if max_pages is not None:
            try:
                max_pages = int(max_pages)
                if max_pages <= 0:
                    max_pages = None
            except (ValueError, TypeError):
                max_pages = None

        workers = int(options.get("workers", 5) or 5)
        timeout = float(options.get("timeout", 15.0) or 15.0)
        snapshot = bool(options.get("snapshot", True))

        capture_opts = CaptureOptions(
            path_scope=parsed_scope,
            exclude_paths=parsed_exclude,
            site_versions=site_versions,
            max_pages=max_pages,
            workers=workers,
            timeout=timeout,
            snapshot=snapshot,
            output_mode="both",
        )

        def worker():
            start_time = time.monotonic()
            stats = {"discovered": 0, "downloaded": 0, "failed": 0}

            def on_progress(event: ProgressEvent):
                if self._cancel_requested:
                    raise RuntimeError("Capture aborted by user")
                kind = event.kind
                if kind == "discovered":
                    stats["discovered"] = event.count or 0
                elif kind == "downloaded":
                    stats["downloaded"] += 1
                elif kind == "failed":
                    stats["failed"] += 1

                self._emit_to_js(
                    "onCaptureProgress",
                    {
                        "kind": kind,
                        "url": event.url,
                        "title": event.title,
                        "size_kb": event.size_kb,
                        "message": event.message,
                        "count": event.count,
                        "done": stats["downloaded"] + stats["failed"],
                        "total": stats["discovered"],
                        "elapsed": round(time.monotonic() - start_time, 1),
                    },
                )

            try:
                result = capture(url, capture_opts, progress=on_progress)
                duration = time.monotonic() - start_time
                self._last_run = {
                    "url": url,
                    "provider": result.provider,
                    "pages_captured": result.pages_captured,
                    "skipped": result.skipped,
                    "warnings": list(result.warnings),
                    "local_path": str(result.local_path) if result.local_path else None,
                    "library_path": str(result.library_path) if result.library_path else None,
                    "book_file": str(result.book_file) if result.book_file else None,
                    "manifest_file": str(result.manifest_file) if result.manifest_file else None,
                    "version_id": result.version_id,
                    "duration_s": round(duration, 2),
                    "stats": stats,
                }
                self._emit_to_js("onCaptureDone", {"success": True, "result": self._last_run})
            except Exception as exc:
                duration = time.monotonic() - start_time
                err_msg = str(exc)
                is_cancelled = "aborted" in err_msg.lower() or "cancel" in err_msg.lower()
                self._last_run = {
                    "url": url,
                    "error": err_msg,
                    "cancelled": is_cancelled,
                    "duration_s": round(duration, 2),
                    "stats": stats,
                }
                self._emit_to_js(
                    "onCaptureDone",
                    {"success": False, "error": err_msg, "cancelled": is_cancelled},
                )

        self._active_thread = threading.Thread(target=worker, daemon=True)
        self._active_thread.start()
        return {"success": True}

    def cancel_capture(self) -> dict[str, Any]:
        """Request the current capture to cancel."""
        self._cancel_requested = True
        return {"success": True}

    # ── Library Management ───────────────────────────────────────────────

    def list_library(self) -> list[dict[str, Any]]:
        """List all captured domains with stats."""
        try:
            entries = []
            for meta in self._storage.list_domains():
                domain = meta.get("domain", "")
                versions = meta.get("versions") or []
                entries.append(
                    {
                        "domain": domain,
                        "title": meta.get("title") or domain,
                        "url": meta.get("url", ""),
                        "provider": meta.get("provider", "generic"),
                        "pages": int(meta.get("total_pages", 0) or 0),
                        "size_bytes": int(meta.get("total_size_kb", 0) or 0) * 1024,
                        "last_crawled": meta.get("last_scraped", ""),
                        "snapshot_count": len(versions),
                        "path": str(self._storage._domain_dir(domain)),
                    }
                )
            entries.sort(key=lambda e: e.get("last_crawled", ""), reverse=True)
            return entries
        except Exception:
            return []

    def get_library_doc(self, domain: str) -> dict[str, Any]:
        """Get the full book content and page tree for a domain."""
        try:
            doc_dir = self._storage._domain_dir(domain)
            book_path = doc_dir / "docs.md"
            if not book_path.exists():
                book_path = doc_dir / "book.md"

            book_content = (
                book_path.read_text(encoding="utf-8", errors="replace")
                if book_path.exists()
                else ""
            )

            pages_dir = doc_dir / "pages"
            pages_list = []
            if pages_dir.exists():
                for md_file in pages_dir.rglob("*.md"):
                    rel = md_file.relative_to(pages_dir).as_posix()
                    pages_list.append(
                        {
                            "relpath": rel,
                            "path": str(md_file),
                            "size": md_file.stat().st_size,
                        }
                    )

            return {
                "success": True,
                "domain": domain,
                "book_content": book_content,
                "pages": sorted(pages_list, key=lambda x: x["relpath"]),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def read_file(self, file_path: str) -> dict[str, Any]:
        """Read a single markdown page."""
        try:
            p = Path(file_path)
            if not p.exists() or not p.is_file():
                return {"success": False, "error": "File not found"}
            content = p.read_text(encoding="utf-8", errors="replace")
            return {"success": True, "content": content, "filename": p.name}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def delete_domain(self, domain: str) -> dict[str, Any]:
        """Delete a domain from the library and search index."""
        try:
            res = self._storage.delete_domain(domain)
            try:
                SearchIndex().delete_domain(domain)
            except Exception:
                pass
            return {"success": res}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def open_local_folder(self, target: str) -> dict[str, Any]:
        """Open a directory or file in Windows Explorer."""
        try:
            p = Path(target)
            if not p.is_absolute():
                if self._storage.domain_exists(target):
                    p = self._storage._domain_dir(target)
                else:
                    p = Path.cwd() / target

            if p.is_file():
                folder = p.parent
            else:
                folder = p

            if not folder.exists():
                folder = Path.cwd()

            if sys.platform == "win32":
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            return {"success": True}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ── Search ───────────────────────────────────────────────────────────

    def search_docs(self, query: str, domain: str | None = None) -> list[dict[str, Any]]:
        """Run SQLite FTS5 search across all or a single domain."""
        query = (query or "").strip()
        if not query:
            return []
        try:
            hits = SearchIndex().search(
                query,
                domain=domain if domain and domain != "all" else None,
            )
            return [
                {
                    "domain": h["domain"],
                    "url": h["url"],
                    "title": h["title"],
                    "section_heading": h.get("section_heading", ""),
                    "snippet": h["snippet"],
                    "rank": round(abs(float(h.get("rank", 0.0))), 2),
                }
                for h in hits
            ]
        except Exception:
            return []

    # ── Snapshots & Diff ─────────────────────────────────────────────────

    def list_snapshots(self, domain: str) -> list[dict[str, Any]]:
        """List snapshot versions for *domain*."""
        try:
            meta = self._storage.get_metadata(domain)
            if not meta:
                return []
            snapshots = []
            for v in reversed(meta.get("versions") or []):
                snapshots.append(
                    {
                        "version_id": v.get("version", "?"),
                        "created_at": v.get("timestamp", ""),
                        "pages": int(v.get("pages", 0) or 0),
                        "size_bytes": int(v.get("size_kb", 0) or 0) * 1024,
                    }
                )
            return snapshots
        except Exception:
            return []

    def diff_snapshots(
        self, domain: str, old_version: str, new_version: str
    ) -> dict[str, Any]:
        """Compute diff between two snapshots."""
        try:
            old_text = self._storage.load_doc_version(domain, old_version) or ""
            new_text = self._storage.load_doc_version(domain, new_version) or ""

            diff_lines = list(
                difflib.unified_diff(
                    old_text.splitlines(),
                    new_text.splitlines(),
                    fromfile=f"{domain} ({old_version})",
                    tofile=f"{domain} ({new_version})",
                    lineterm="",
                )
            )
            added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
            removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))

            return {
                "success": True,
                "domain": domain,
                "old_version": old_version,
                "new_version": new_version,
                "pages_added": 0,
                "pages_removed": 0,
                "pages_changed": 1 if diff_lines else 0,
                "lines_added": added,
                "lines_removed": removed,
                "changes": [
                    {
                        "url": domain,
                        "status": "changed" if diff_lines else "unchanged",
                        "lines_added": added,
                        "lines_removed": removed,
                        "diff_text": "\n".join(diff_lines[:300]),
                    }
                ] if diff_lines else [],
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ── Export Studio ────────────────────────────────────────────────────

    def export_doc(
        self, domain: str, format_type: str, custom_path: str | None = None
    ) -> dict[str, Any]:
        """Export documentation for *domain* to markdown bundle, PDF, or JSONL."""
        try:
            doc_dir = self._storage._domain_dir(domain)
            if not doc_dir.exists():
                return {"success": False, "error": f"Domain {domain} not found in library."}

            book_path = doc_dir / "docs.md"
            if not book_path.exists():
                book_path = doc_dir / "book.md"

            fmt = (format_type or "md").lower()
            out_base = Path(custom_path) if custom_path else Path.cwd() / "exports"
            out_base.mkdir(parents=True, exist_ok=True)

            if fmt == "md":
                dest = out_base / f"{domain}-book.md"
                if book_path.exists():
                    shutil.copy2(book_path, dest)
                    return {"success": True, "path": str(dest), "format": "md"}
                return {"success": False, "error": "Source book.md not found"}

            elif fmt == "pdf":
                from gitbook_downloader.utils.export import export_to_pdf
                dest = out_base / f"{domain}-docs.pdf"
                msg = export_to_pdf(book_path, dest)
                return {"success": True, "path": str(dest), "message": msg, "format": "pdf"}

            elif fmt == "jsonl":
                dest = out_base / f"{domain}-rag.jsonl"
                pages_dir = doc_dir / "pages"
                records = []
                if pages_dir.exists():
                    for md_file in pages_dir.rglob("*.md"):
                        text = md_file.read_text(encoding="utf-8", errors="replace")
                        rel = md_file.relative_to(pages_dir).as_posix()
                        records.append(
                            {
                                "id": f"{domain}/{rel}",
                                "domain": domain,
                                "path": rel,
                                "text": text,
                            }
                        )
                with open(dest, "w", encoding="utf-8") as fh:
                    for rec in records:
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                return {
                    "success": True,
                    "path": str(dest),
                    "count": len(records),
                    "format": "jsonl",
                }
            else:
                return {"success": False, "error": f"Unsupported format: {format_type}"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ── Diagnostics & Info ───────────────────────────────────────────────

    def get_diagnostics(self) -> dict[str, Any]:
        """Return details of the last crawl run."""
        return self._last_run or {}

    def get_system_info(self) -> dict[str, Any]:
        """Return app metadata."""
        return {
            "version": "9.0.0b1",
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "library_dir": str(self._storage.base),
            "cwd": str(Path.cwd()),
        }
