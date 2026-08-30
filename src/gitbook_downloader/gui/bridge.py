"""Python <-> JavaScript bridge for the Desktop GUI."""

from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import queue
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from .. import __version__
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
    def __init__(self, window=None, storage_manager=None) -> None:
        self._window = window
        self._storage = storage_manager or StorageManager()
        self._cancel_requested = False
        self._cancel_event = threading.Event()
        self._active_thread: threading.Thread | None = None
        self._last_run: dict[str, Any] | None = None
        # Phase 4 step 3: marshal _emit_to_js calls onto the UI thread.
        # PyWebView's `window.evaluate_js` must be called from the UI thread;
        # the capture worker thread used to call it directly, racing the
        # WebView2 message loop on Windows. The drain thread below
        # consumes the queue and is the only caller of evaluate_js.
        self._emit_queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self._emit_drain_stop = threading.Event()
        self._emit_drain_thread: threading.Thread | None = None

    def start_emit_drain(self) -> None:
        """Start the queue-drain thread (call once after window is set)."""
        if self._emit_drain_thread is not None and self._emit_drain_thread.is_alive():
            return
        self._emit_drain_stop.clear()
        self._emit_drain_thread = threading.Thread(
            target=self._drain_emit_queue,
            name="ApiBridge.emit-drain",
            daemon=True,
        )
        self._emit_drain_thread.start()

    def _drain_emit_queue(self) -> None:
        """Consume _emit_queue and call evaluate_js on the UI thread side."""
        while not self._emit_drain_stop.is_set():
            try:
                func_name, data = self._emit_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if self._window is None:
                continue
            payload = json.dumps(data)
            js_code = f"if (window.{func_name}) {{ window.{func_name}({payload}); }}"
            try:
                self._window.evaluate_js(js_code)
            except Exception:
                # Swallow JS errors; emit is best-effort progress reporting.
                pass

    def _emit_to_js(self, func_name: str, data: Any) -> None:
        """Queue a JS callback for the drain thread to fire on the UI thread.

        Safe to call from any thread (worker or UI). Returns immediately;
        actual evaluate_js happens on the drain thread.
        """
        if self._window is None:
            return
        try:
            self._emit_queue.put_nowait((func_name, data))
        except queue.Full:  # pragma: no cover - queue has no max size
            pass

    def set_window(self, window) -> None:
        self._window = window
        # Auto-start the emit-drain thread once a window is attached.
        self.start_emit_drain()

    def cleanup(self) -> None:
        """Called when WebView window closes or app exits."""
        self._cancel_requested = True
        self._cancel_event.set()
        if self._active_thread and self._active_thread.is_alive():
            self._active_thread.join(timeout=0.5)
        try:
            self._storage.clear_all_locks(force=False)
        except Exception:
            pass
        # Stop the drain thread.
        self._emit_drain_stop.set()
        if self._emit_drain_thread and self._emit_drain_thread.is_alive():
            self._emit_drain_thread.join(timeout=0.5)

    def detect(self, url: str) -> dict[str, Any]:
        """Detect the documentation provider and site versions for *url*."""
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            return {"success": False, "error": "Enter a valid http(s) URL"}
        try:
            sess = requests.Session()
            sess.headers["User-Agent"] = f"gitbook-downloader/{__version__}"
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

    def get_lock_status(self, domain: str | None = None) -> dict[str, Any]:
        """Query status of active locks and current worker thread."""
        try:
            all_locks = self._storage.list_active_locks()
            target_lock = None
            if domain:
                norm_domain = domain.strip().lower().removeprefix("http://").removeprefix("https://").split("/")[0].removeprefix("www.")
                for l in all_locks:
                    if l.get("domain") == norm_domain:
                        target_lock = l
                        break

            return {
                "success": True,
                "active_locks": all_locks,
                "has_active_locks": len(all_locks) > 0,
                "domain_locked": target_lock is not None and not target_lock.get("is_stale"),
                "target_lock": target_lock,
                "is_worker_alive": bool(self._active_thread and self._active_thread.is_alive()),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "active_locks": []}

    # ── Capture Execution ────────────────────────────────────────────────

    def start_capture(self, url: str, options: dict[str, Any]) -> dict[str, Any]:
        """Launch a capture job in a dedicated background worker thread."""
        if self._active_thread and self._active_thread.is_alive():
            if self._cancel_requested:
                self._active_thread.join(timeout=1.5)
            if self._active_thread.is_alive():
                return {"success": False, "error": "A capture is already running"}

        self._cancel_requested = False
        self._cancel_event.clear()

        raw_scope = options.get("path_scope") or ""
        parsed_scope = tuple(
            s.strip() for s in str(raw_scope).split(",") if s.strip()
        )
        raw_exclude = options.get("exclude_paths") or ""
        parsed_exclude = tuple(
            s.strip() for s in str(raw_exclude).split(",") if s.strip()
        )
        site_versions = options.get("site_versions")
        if isinstance(site_versions, (list, tuple)):
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
        render = bool(options.get("render", False))

        output_mode = str(options.get("output_mode", "library") or "library")
        if output_mode not in ("library", "both", "local"):
            output_mode = "library"

        capture_opts = CaptureOptions(
            path_scope=parsed_scope,
            exclude_paths=parsed_exclude,
            site_versions=site_versions,
            max_pages=max_pages,
            workers=workers,
            timeout=timeout,
            snapshot=snapshot,
            output_mode=output_mode,
            render=render,
            cancel_check=lambda: self._cancel_event.is_set(),
        )

        def worker():
            start_time = time.monotonic()
            stats = {"discovered": 0, "downloaded": 0, "failed": 0}

            def on_progress(event: ProgressEvent):
                if self._cancel_event.is_set() or self._cancel_requested:
                    raise RuntimeError("Capture aborted by user")
                kind = event.kind
                if kind == "discovered":
                    stats["discovered"] = event.count or 0
                elif kind == "downloaded":
                    stats["downloaded"] += 1
                elif kind == "failed":
                    stats["failed"] += 1

                done_count = stats["downloaded"] + stats["failed"]
                total_count = max(stats["discovered"], done_count)
                percent = round((done_count / total_count) * 100) if total_count > 0 else 0
                percent = min(100, max(0, percent))

                self._emit_to_js(
                    "onCaptureProgress",
                    {
                        "kind": kind,
                        "url": event.url,
                        "title": event.title,
                        "size_kb": event.size_kb,
                        "message": event.message or (f"Downloaded: {event.title}" if kind == "downloaded" else f"Found: {event.url}"),
                        "count": event.count,
                        "done": done_count,
                        "downloaded": stats["downloaded"],
                        "failed": stats["failed"],
                        "discovered": stats["discovered"],
                        "total": total_count,
                        "percent": percent,
                        "elapsed": round(time.monotonic() - start_time, 1),
                    },
                )

            try:
                result = capture(url, capture_opts, progress=on_progress)
                duration = time.monotonic() - start_time

                # Emit warnings to JS progress log
                for warning_msg in result.warnings:
                    self._emit_to_js(
                        "onCaptureProgress",
                        {
                            "kind": "failed" if result.pages_captured == 0 else "warn",
                            "message": f"⚠ {warning_msg}",
                            "elapsed": round(duration, 1),
                        },
                    )

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
                self._emit_to_js(
                    "onCaptureDone",
                    {
                        "success": result.pages_captured > 0,
                        "error": result.warnings[0] if (result.pages_captured == 0 and result.warnings) else None,
                        "result": self._last_run,
                        "pages_downloaded": result.pages_captured,
                        "stats": stats,
                    },
                )
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
                    {
                        "success": False,
                        "error": err_msg,
                        "cancelled": is_cancelled,
                        "stats": stats,
                    },
                )

        self._active_thread = threading.Thread(target=worker, daemon=True)
        self._active_thread.start()
        return {"success": True}

    def cancel_capture(self) -> dict[str, Any]:
        """Request the current capture to cancel immediately."""
        self._cancel_requested = True
        self._cancel_event.set()
        if self._active_thread and self._active_thread.is_alive():
            self._active_thread.join(timeout=1.0)
        return {"success": True}

    def reset_capture(self) -> dict[str, Any]:
        """Forcefully reset the capture thread state and clear all active locks."""
        self._cancel_requested = True
        self._cancel_event.set()
        if self._active_thread and self._active_thread.is_alive():
            self._active_thread.join(timeout=1.0)
        self._active_thread = None
        cleared = self._storage.clear_all_locks(force=True)
        return {"success": True, "cleared_locks": cleared}


    # ── Library Management ───────────────────────────────────────────────

    def list_library(self) -> list[dict[str, Any]]:
        """List all captured domains with stats."""
        try:
            entries = []
            for meta in self._storage.list_domains():
                domain = meta.get("domain", "")
                versions = meta.get("versions") or []
                try:
                    snapshots = self.list_snapshots(domain)
                    snapshot_versions = [s.get("version_id", "?") for s in snapshots]
                except Exception:
                    snapshot_versions = []
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
                        "snapshots": snapshot_versions,
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
                for md_file in sorted(pages_dir.rglob("*.md")):
                    rel = md_file.relative_to(pages_dir).as_posix()
                    title = md_file.stem
                    try:
                        first_lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()[:5]
                        for l in first_lines:
                            if l.startswith("# "):
                                title = l[2:].strip()
                                break
                    except Exception:
                        pass
                    pages_list.append(
                        {
                            "title": title,
                            "relpath": rel,
                            "path": str(md_file),
                            "size": md_file.stat().st_size,
                        }
                    )

            if not book_content and pages_list:
                parts = []
                for p in pages_list:
                    p_path = Path(p["path"])
                    if p_path.exists():
                        parts.append(p_path.read_text(encoding="utf-8", errors="replace"))
                book_content = "\n\n---\n\n".join(parts)

            return {
                "success": True,
                "domain": domain,
                "title": domain,
                "content": book_content,
                "book_content": book_content,
                "folder": str(doc_dir),
                "path": str(doc_dir),
                "pages": pages_list,
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

    def rename_domain(self, old_domain: str, new_domain: str) -> dict[str, Any]:
        """Rename a domain in the library and search index."""
        try:
            old_domain = (old_domain or "").strip()
            new_domain = (new_domain or "").strip()
            if not old_domain or not new_domain:
                return {"success": False, "error": "Domain name cannot be empty."}
            if old_domain == new_domain:
                return {"success": True, "domain": new_domain}

            res = self._storage.rename_domain(old_domain, new_domain)
            if not res:
                return {"success": False, "error": f"Could not rename '{old_domain}' to '{new_domain}'. Destination may already exist."}

            try:
                SearchIndex().rename_domain(old_domain, new_domain)
            except Exception:
                pass
            return {"success": True, "domain": new_domain}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def open_folder(self, target: str) -> dict[str, Any]:
        """Open a directory or highlight a file in Windows Explorer / Finder."""
        try:
            p = Path(target)
            if not p.is_absolute():
                if self._storage.domain_exists(target):
                    p = self._storage._domain_dir(target)
                else:
                    p = Path.cwd() / target

            if not p.exists():
                if p.parent.exists():
                    p = p.parent
                else:
                    p = self._storage.root_dir

            if sys.platform == "win32":
                if p.is_file():
                    subprocess.Popen(f'explorer.exe /select,"{p}"', shell=True)
                else:
                    os.startfile(str(p))
            elif sys.platform == "darwin":
                if p.is_file():
                    subprocess.Popen(["open", "-R", str(p)])
                else:
                    subprocess.Popen(["open", str(p)])
            else:
                folder = p.parent if p.is_file() else p
                subprocess.Popen(["xdg-open", str(folder)])
            return {"success": True, "path": str(p)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # (open_local_folder alias removed in Phase 4 step 2: dead method,
    # never called from the TS surface, never typed in the frontend.)
    def open_file(self, target: str) -> dict[str, Any]:
        """Open a document / export file directly with the operating system's default application."""
        try:
            p = Path(target)
            if not p.is_absolute():
                p = Path.cwd() / target

            if not p.exists():
                return {"success": False, "error": f"File not found: {p}"}

            if sys.platform == "win32":
                os.startfile(str(p))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return {"success": True, "path": str(p)}
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

            # Synthesize book.md if needed
            if not book_path.exists():
                pages_dir = doc_dir / "pages"
                if pages_dir.exists():
                    combined = []
                    for p_file in sorted(pages_dir.rglob("*.md")):
                        combined.append(p_file.read_text(encoding="utf-8", errors="replace"))
                    if combined:
                        book_path = doc_dir / "docs.md"
                        book_path.write_text("\n\n---\n\n".join(combined), encoding="utf-8")

            fmt = (format_type or "md").lower().strip()

            # Output base determination
            if custom_path:
                out_base = Path(custom_path)
            else:
                cwd_str = str(Path.cwd()).lower()
                if "system32" in cwd_str or "syswow64" in cwd_str or "windows" in cwd_str:
                    out_base = Path.home() / "Downloads" / "gitbook-exports"
                else:
                    out_base = Path.cwd() / "exports"

            out_base.mkdir(parents=True, exist_ok=True)

            if fmt == "md":
                dest = out_base / f"{domain}-book.md"
                if book_path.exists():
                    shutil.copy2(book_path, dest)
                    return {"success": True, "path": str(dest), "format": "md"}
                return {"success": False, "error": "Source documentation pages not found to build markdown"}

            elif fmt == "pdf":
                from gitbook_downloader.utils.export import export_to_pdf
                if not book_path.exists():
                    return {"success": False, "error": "No markdown content found to convert to PDF"}
                dest = out_base / f"{domain}-docs.pdf"
                actual_path = export_to_pdf(book_path, dest)
                return {"success": True, "path": str(actual_path), "format": "pdf"}

            elif fmt == "jsonl":
                dest = out_base / f"{domain}-rag.jsonl"
                pages_dir = doc_dir / "pages"
                records = []
                if pages_dir.exists():
                    for md_file in sorted(pages_dir.rglob("*.md")):
                        text = md_file.read_text(encoding="utf-8", errors="replace")
                        rel = md_file.relative_to(pages_dir).as_posix()
                        title = md_file.stem
                        for l in text.splitlines()[:5]:
                            if l.startswith("# "):
                                title = l[2:].strip()
                                break
                        records.append(
                            {
                                "id": f"{domain}/{rel}",
                                "domain": domain,
                                "title": title,
                                "path": rel,
                                "text": text,
                                "length": len(text),
                            }
                        )

                if not records and book_path.exists():
                    full_text = book_path.read_text(encoding="utf-8", errors="replace")
                    sections = full_text.split("\n# ")
                    for i, sec in enumerate(sections):
                        if not sec.strip():
                            continue
                        sec_text = ("# " + sec) if i > 0 else sec
                        first_line = sec_text.splitlines()[0].replace("#", "").strip()
                        records.append(
                            {
                                "id": f"{domain}/section_{i}",
                                "domain": domain,
                                "title": first_line or f"Section {i}",
                                "path": f"section_{i}.md",
                                "text": sec_text,
                                "length": len(sec_text),
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
            "name": "DocHarvest",
            "version": __version__,
            "engine": f"DocHarvest Engine v{__version__} (AST + FastMCP v2 + fpdf2)",
            "author": "Rohan Shetty",
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "library_dir": str(self._storage.base),
            "cwd": str(Path.cwd()),
        }

    def is_render_available(self) -> dict[str, Any]:
        """Check if Playwright headless browser rendering is installed and available."""
        try:
            from ..utils.renderer import is_render_available
            return {"available": is_render_available()}
        except Exception:
            return {"available": False}
