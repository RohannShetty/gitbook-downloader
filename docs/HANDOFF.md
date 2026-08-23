# GitBook Downloader v9.0.1 Handoff & Architecture Memory

This document serves as the canonical handoff and knowledge-transfer record for **GitBook Downloader v9.0.1**. It outlines all architectural improvements, engine hardening mechanisms, UI overhaul decisions, known edge-cases, and instructions for continuing development.

---

## 1. Executive Summary & Release Metadata

* **Version**: `9.0.1` (Bumped from `9.0.0`)
* **Git Tag**: `v9.0.1`
* **Target Branches**: `main` and `master` on `origin` (GitHub: `RohannShetty/gitbook-downloader`)
* **Standalone Executable**: `dist/gitbook-dl.exe` (32.9 MB, bundled with React 18 + Vite web assets)
* **Test Suite Status**: 484 Passed, 2 Skipped (optional `mcp` library tests), 0 Failures.

---

## 2. Codebase Audit & Engine Hardening Architecture

### A. Self-Recovering Domain Locks & Cross-Platform PID Validation
* **Source Location**: [`src/gitbook_downloader/storage/manager.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/storage/manager.py)
* **Problem**: Aborted or interrupted crawling processes previously left `.lock` files in `~/.gitbook-downloader/locks/<domain>.lock`, permanently blocking subsequent runs with `LockHeldError` unless manually deleted.
* **Solution**:
  1. Implemented cross-platform process validation:
     * **Windows**: `ctypes.windll.kernel32.OpenProcess` and `GetExitCodeProcess` verifying `STILL_ACTIVE (259)`.
     * **POSIX**: `os.kill(pid, 0)` checking for `ESRCH`.
  2. `DomainLock._is_stale()` automatically detects if the process holding the lock has terminated, releasing the lock file immediately.
  3. Registered `atexit` cleanup handler `_cleanup_process_locks()` to guarantee that any locks acquired by the current Python runtime are cleaned up on clean or error exits.
  4. Added `StorageManager.list_active_locks()` and `StorageManager.clear_all_locks(force=True)`.

### B. Single-Page Application (SPA) Auto-Scoping & Fast Crawling
* **Source Location**: [`src/gitbook_downloader/engine.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/engine.py)
* **Problem**: Sites like `https://pi.dev/docs/latest` (custom Next.js/React SPAs) lack `sitemap.xml` and `llms.txt`. When crawling without an explicit `--path-scope`, the BFS crawler discovered the navbar root (`/`) and wandered off into marketing pages (`/news`, `/models`, `/packages`), sequentially crawling hundreds of non-documentation pages.
* **Solution**:
  1. `_bfs_crawl` automatically checks if `path_scope` was provided. If not, and the starting URL has a subpath (e.g. `/docs/latest`), it bounds the BFS link extraction to `(start_path,)`.
  2. Real-time discovery progress callbacks (`phase: "discovered"`) are emitted during `_bfs_crawl` so the UI terminal and stats update in real time instead of remaining silent.
  3. **Benchmark**: `https://pi.dev/docs/latest` crawls and downloads all 30 pages in **18.39 seconds**.

### C. Cooperative Non-Blocking Cancellation
* **Source Locations**: [`src/gitbook_downloader/engine.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/engine.py), [`src/gitbook_downloader/gui/bridge.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/gui/bridge.py), [`src/gitbook_downloader/gui/app.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/gui/app.py)
* **Problem**: Clicking "Cancel" or closing the window could leave background threads running as zombies.
* **Solution**:
  1. `stream_download` and `_bfs_crawl` accept `cancel_check: Callable[[], bool]`.
  2. `ThreadPoolExecutor` immediately invokes `executor.shutdown(wait=False, cancel_futures=True)` when cancellation is requested.
  3. PyWebView window closing event is connected to `bridge.cleanup()` in `app.py`.

### D. Socket Handshake Timeouts
* **Source Location**: [`src/gitbook_downloader/utils/retry.py`](file:///D:/gitbook-downloader/src/gitbook_downloader/utils/retry.py)
* **Solution**: `TimeoutHTTPAdapter` automatically injects `DEFAULT_CONNECT_TIMEOUT = 5.0s` and per-request read timeouts on all outgoing HTTP connections to prevent hung TCP handshakes.

---

## 3. UI Overhaul (Premium Shadcn & Motion)

### A. Design Contract & Tokens
* **Source Location**: [`frontend/src/index.css`](file:///D:/gitbook-downloader/frontend/src/index.css)
* **Features**:
  * Dark theme palette using clean zinc/slate tokens with subtle glassmorphic styling (`.glass-panel`, `.glass-card`).
  * Micro-interactions (`.interactive-scale`) with active press states and hover highlights.
  * Custom glowing indicators (`.glow-cyan`, `.glow-emerald`, `.glow-rose`).

### B. Capture Studio View
* **Source Location**: [`frontend/src/views/CaptureStudio.tsx`](file:///D:/gitbook-downloader/frontend/src/views/CaptureStudio.tsx)
* **Features**:
  * **Active Storage Lock Banner**: Real-time lock status badge displaying PID, domain, and age with an instant "Unlock & Force Reset" button.
  * **Action Controls**: High-contrast glowing "Start Capture", pulsing red "Cancel Capture", and dedicated "Force Reset" CTA.
  * **Telemetry Dashboard**: Animated radial SVG progress ring with pages/second speed and 4 live telemetry cards.
  * **Filterable Live Terminal**: Real-time search, log level filters (`All`, `Downloaded`, `Discovered`, `Errors`), one-click log copying, and clear terminal button.

### C. Supporting Views & Components
* **Document Library** ([`frontend/src/views/LibraryView.tsx`](file:///D:/gitbook-downloader/frontend/src/views/LibraryView.tsx)): Sorted grid by recent date, pages, size, or domain, with tailored provider badges.
* **Export Studio** ([`frontend/src/views/ExportView.tsx`](file:///D:/gitbook-downloader/frontend/src/views/ExportView.tsx)): Format cards for RAG JSONL vector datasets, PDF printable handbooks, and unified markdown (`book.md`).
* **Snapshot Diff Studio** ([`frontend/src/views/DiffView.tsx`](file:///D:/gitbook-downloader/frontend/src/views/DiffView.tsx)): Unified diff viewer with additions/removals counters.
* **Search Studio** ([`frontend/src/views/SearchView.tsx`](file:///D:/gitbook-downloader/frontend/src/views/SearchView.tsx)): SQLite FTS5 BM25 search with snippet previews and one-click "Read in Studio" modal.
* **Diagnostics** ([`frontend/src/views/DiagnosticsView.tsx`](file:///D:/gitbook-downloader/frontend/src/views/DiagnosticsView.tsx)): Real-time lock inspector and runtime environment telemetry.

---

## 4. How to Build & Test

### Running the Python Backend Tests
```powershell
pytest
```
*Expected output: 484 passed, 2 skipped (MCP optional tests)*

### Building the Frontend Assets
```powershell
cd frontend
npm run build
```
*Outputs compiled assets into `src/gitbook_downloader/gui/web/`*

### Building the Standalone Executable
```powershell
python build_exe.py
```
*Outputs `dist/gitbook-dl.exe` (32.9 MB)*

### Launching the Desktop GUI
```powershell
.\dist\gitbook-dl.exe --gui
# Or in development:
python -m gitbook_downloader.cli --gui
```
