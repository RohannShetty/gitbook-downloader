# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [10.0.0] - 2026-08-23

### 🌾 The DocHarvest Rebrand, GitHub Pages Showcase Site & Release Automation

Version 10.0.0 marks the official rebranding to **DocHarvest** (*Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*), introducing a modern React + shadcn/ui showcase landing site, single-job release automation with structured markdown release notes, and a complete multi-channel distribution kit.

### Added & Improved in v10.0.0
- 🏷️ **DocHarvest Brand Identity & Marketing Engine**:
  - Transitioned project identity from legacy single-purpose downloader to the comprehensive **DocHarvest** AI knowledge engineering platform.
  - Canonical `.agents/product-marketing.md` established across all three core ICPs (AI/RAG engineers, offline developers, and DevOps/archival teams).
- 🌐 **React + shadcn/ui GitHub Pages Showcase Site**:
  - Fully responsive landing page in `docs/` built with React 18, Vite, Tailwind CSS, and shadcn/ui design tokens.
  - Interactive Doc-Type selector (GitBook, Mintlify, Docusaurus, Nextra, ReadMe, VitePress), live terminal simulator, and direct binary download matrix.
  - Automated `.github/workflows/pages.yml` deployment workflow.
- 🔧 **Single-Job Release Workflow & Automated Notes Generation**:
  - Refactored `.github/workflows/build-release.yml` to decouple binary builds from release publishing.
  - Added `scripts/generate_release_notes.py` for automated categorization (Features, Fixes, Architecture, Downloads, and SHA-256 checksums), eliminating duplicate changelog links on GitHub.
- 📢 **Comprehensive Social Launch Kit & Distribution Strategy**:
  - Multi-platform launch templates for X/Twitter, Reddit (`r/LocalLLaMA`, `r/Python`, `r/selfhosted`, `r/OpenAI`), Hacker News (Show HN), and Dev.to under `marketing/`.
  - Detailed `docs/SEO_GUIDE.md` for GitHub repository topics, description, and OpenGraph social preview assets.

---

## [9.0.1] - 2026-08-23

### 🛡️ Engine Hardening, SPA Fast Crawling, Self-Recovering Locks & Premium UI Overhaul

Version 9.0.1 delivers robust multi-process lock safety with automatic dead-process PID detection, high-performance auto-scoping for single-page documentation apps (e.g. `pi.dev`), real-time discovery telemetry, and an overhauled premium Shadcn UI design contract with motion transitions.

### Added & Improved in v9.0.1
- 🔒 **Self-Recovering Domain Locks & Cross-Platform PID Liveness**:
  - Implemented cross-platform OS process validation (`is_process_running(pid)` with Windows `OpenProcess`/`GetExitCodeProcess` and POSIX `os.kill(pid, 0)`).
  - Automatically reclaims abandoned lock files if the owning process crashes or terminates unexpectedly.
  - Added `StorageManager.list_active_locks()`, `StorageManager.clear_all_locks()`, and `atexit` auto-cleanup handlers.
- 🧭 **Intelligent Path-Scope Auto-Inference for Single-Page Apps (SPAs)**:
  - When capturing targets without sitemaps/llms.txt (such as `https://pi.dev/docs/latest`), the crawler automatically bounds discovery to the URL's subpath prefix, preventing runaway crawls into marketing homepages, news, and external assets.
  - `_bfs_crawl` now emits live discovery events (`phase: "discovered"`) in real time to the GUI telemetry terminal.
- ⚡ **Cooperative Non-Blocking Cancellation & Zombie Thread Elimination**:
  - Implemented cooperative `cancel_check: Callable[[], bool]` across `stream_download` and `_bfs_crawl`.
  - Immediate `ThreadPoolExecutor.shutdown(wait=False, cancel_futures=True)` on cancel request, releasing system resources without hung threads.
- 🔌 **Socket Connection Timeouts**:
  - Injected `DEFAULT_CONNECT_TIMEOUT = 5.0s` into `TimeoutHTTPAdapter` to eliminate hung TCP socket handshakes.
- 🎨 **Premium Shadcn Desktop GUI & Motion Overhaul**:
  - Redesigned **Capture Studio** with glowing status indicators, animated radial progress gauge with live speed metrics (pages/sec), and filterable real-time terminal logs.
  - Added prominent **Active Storage Lock Banner** with one-click **Unlock & Force Reset** action.
  - Upgraded **Document Library**, **Export Studio**, **Snapshot Diff**, **Search Studio**, and **Diagnostics** views with refined glassmorphism cards and micro-interactions.

---

## [9.0.0] - 2026-08-23

### 🚀 Major Stable Release: Modern shadcn/ui Desktop Architecture, AI RAG Pipeline & Universal Scoper

Version 9.0 marks the official stable release of **GitBook Downloader v9**, featuring a complete frontend re-engineering with **React 18 + Vite + Tailwind CSS + shadcn/ui**, pure Python PDF generation via `fpdf2`, native Windows Explorer integration, automated documentation-root scoping for subpage URLs (e.g. `ui.shadcn.com/docs/installation`), and AI-ready vector JSONL RAG export pipelines.

### Added & Improved in v9.0 Stable
- 🎨 **shadcn/ui Design System**:
  - Re-architected desktop frontend using Radix UI primitives and shadcn zinc dark/light tokens.
  - Collapsible sidebar with active indicators, badge telemetry, and theme switching.
  - Universal `Ctrl+K` / `Cmd+K` Command Palette for rapid view switching and document lookup.
  - Light/Dark theme-adaptive Sonner toast notification system.
- ⚡ **Pure Python PDF Generation Engine (`fpdf2`)**:
  - Zero C/GTK+ external dependencies: generates true binary `%PDF-` document books with syntax-highlighted code blocks, clean typography, headers, and footers directly from markdown.
- 📁 **Native Windows Explorer & System Reader Integration**:
  - Added direct Windows Explorer highlighting (`explorer.exe /select,"<path>"`) and system-associated document viewing for exported PDFs, Markdown files, and JSONL datasets.
  - Added in-app split Document Reader with live page browsing, filtering, and single-click markdown copying.
- 🔍 **Universal Doc-Root Auto-Expansion Engine**:
  - When given sub-page URLs (such as `https://ui.shadcn.com/docs/installation`), the engine automatically detects and expands to the documentation root (`/docs`), capturing all related documentation pages unless an explicit `--path-scope` is requested.
- 📦 **RAG & AI Vector Dataset Export Studio**:
  - Direct export of offline documentation sets into structured JSONL format tailored for LangChain, LlamaIndex, OpenAI embeddings, and ChromaDB.
- 🛡️ **Zero-Crash Worker Lifecycle & Thread Safety**:
  - Safe stop/cancel/restart state machine preventing "capture is already running" race conditions.
  - 100% test coverage with 484 unit and integration tests.

---

## [9.0.0-beta.1] - 2026-08-23

### ⚡ v9.0 Beta Release: React + shadcn/ui Desktop Architecture & RAG Export Studio

Version 9.0 Beta introduces a complete frontend rewrite powered by **React 18 + Vite + Tailwind CSS + shadcn/ui** running inside Edge WebView2, featuring a collapsible sidebar, universal `Ctrl+K` command palette, batch capture queue, in-app split Markdown reader with Table of Contents, RAG/AI vector JSONL export studio, and zero-runtime standalone Windows packaging.

### Added
- **Complete shadcn/ui React Frontend Architecture (`./frontend`)**:
  - Rebuilt desktop interface using Radix UI primitives and shadcn zinc design tokens.
  - **Collapsible Modern Sidebar (`AppSidebar`)**: Sleek navigation with active status indicators, badge counts, theme switcher, and command menu shortcuts.
  - **Global Command Menu (`Ctrl+K` / `Cmd+K`)**: Fast keyboard-driven navigation across views, direct library doc opening, and storage actions.
  - **Batch Capture Queue**: Queue multiple documentation websites to crawl sequentially in the background.
  - **Export Studio**: One-click export of captured documentation sets directly to **JSONL** (formatted for LangChain, LlamaIndex, OpenAI embeddings, ChromaDB), **PDF**, or concatenated **book.md**.
  - **Interactive Split Document Reader**: In-app reader modal with page filtering, table of contents, char count telemetry, and copy-to-clipboard.
  - **Sonner Toast System**: Toast alerts for in-flight crawler notifications and file exports.
- **Python Bridge Extensions (`src/gitbook_downloader/gui/bridge.py`)**:
  - Added `export_doc(domain, format_type, custom_path)` supporting `.md`, `.pdf`, and `.jsonl`.
- **Automated Frontend Build Pipeline (`build_exe.py`)**:
  - `build_exe.py` automatically runs Vite compilation before PyInstaller packaging for seamless standalone distribution.

---

## [8.0.0] - 2026-08-23

### 🚀 Major Release: Modern Windows Desktop GUI Application & Standalone Executable

Version 8.0 transforms **GitBook Downloader** from a command-line utility into a modern **Windows Desktop GUI Software Application** powered by Edge WebView2 (`pywebview`), featuring 60fps motion animations, a glowing radial progress gauge, live crawl streaming logs, in-app Markdown reader, instant full-text search studio, snapshot diff visualizer, and standalone single-file executable distribution.

![GitBook Downloader v8 Capture Studio](assets/capture_studio.png)

### Added

- **Modern Desktop GUI Application (Edge WebView2 Runtime)**:
  - Native hardware-accelerated Windows application window (`gitbook-dl` or double-clicking the `.exe`).
  - Dark glassmorphic design system (`#090d16` canvas, frosted glass blur, electric cyan `#06b6d4` & hyper sapphire `#3b82f6` accents, custom light/dark theme toggle).
  - **Dynamic 60fps Motion Progress**:
    - Animated SVG radial circular gauge displaying real-time percentage completion.
    - Animated striped linear progress meter with glowing sweep head.
    - 4 live telemetry stat cards: Discovered URLs, Downloaded Pages, Failed/Skipped Pages, and Elapsed Time counter.
    - **100% Completed Emerald State**: Dynamic shift to vibrant emerald green (`#10b981`) upon crawl completion with glowing completion badges.
  - **Live Syntax-Highlighted Crawl Terminal**:
    - Color-coded live stream (`[DISCOVERED]`, `[DOWNLOADED]`, `[ERROR]`, `[COMPLETE]`) with auto-scroll lock, copy-to-clipboard, and clear controls.
  - **Active In-Flight Cancellation**:
    - Dedicated "Cancel Capture" button and `Esc` keyboard shortcut to immediately abort running crawls safely without data corruption.
  - **Document Library Explorer & Reader**:
    - Real-time catalog of all captured documentation sites, page counts, disk sizes, snapshot histories, and crawl dates.
    - In-app split-screen Markdown Reader modal supporting both full `book.md` viewing and individual page navigation.
    - Instant "Open in Windows Explorer" folder integration.
  - **Search Studio**:
    - Fast SQLite FTS5 documentation search across all downloaded doc sets with keyword match highlighting and relevancy ranking.
  - **Snapshot Diff Visualizer**:
    - Side-by-side and unified version diffing between snapshots.
  - **Diagnostics & Telemetry**:
    - Crawl performance metrics, provider detection evidence rules, and system environment reporting.
- **Multi-Page Stream Parsing**:
  - Added `_parse_pages_from_text` in normalization to reconstruct individual `CapturedPage` instances from streamed multi-page scrapes (e.g. 360+ pages from OpenAlgo).
- **Standalone Windows Executable (`dist/gitbook-dl.exe`)**:
  - Single 23.5 MB self-contained binary bundling Python 3, PyWebView, WebView2 bridge, and all frontend assets with zero external dependencies.
  - **Dual-Mode Launcher**: Bare invocation / double-click opens the Desktop GUI; CLI arguments (e.g. `gitbook-dl capture <url>`) run in headless console mode.

### Changed

- **Direct Enter-to-Download**: Pressing `Enter` in the URL bar initiates provider detection and starts the download immediately.
- **Automatic Library Refresh**: Library catalog and FTS search indexes are automatically updated and populated immediately upon capture completion.
- **Version bump**: Upgraded project version to `v8.0.0` across all metadata, CLI, TUI, and GUI runtime bridges.

---

## [7.0.1] - 2026-08-23

### Fixed

- Fixed character-encoding crashes on Windows PowerShell and Command Prompt when printing Unicode page titles.
- Hardened provider detection fallback when sites return plain text or custom headers.
- Fixed CLI `--preset` argument handling for custom configuration profiles.

---

## [7.0.0] - 2026-08-22

### Added

- **Capture facade** — `gitbook_downloader.api.capture(url, options)` is the single entry point shared by CLI, TUI, GUI, and MCP server.
- **Output contract writer** — Every capture produces four artifacts: a page tree with YAML frontmatter (source URL, title, crawl date, SHA-256 hash, site version), a combined `book.md` with table of contents, and an `llms.txt` manifest.
- **Textual TUI** — Terminal UI with wizard, library browser, search, snapshot diff, and diagnostics screens.
- **TOML presets** — `[defaults]` and `[presets.<name>]` in `gitbook-downloader.toml`.
- **MCP server** — Route all AI agent queries directly through `api.capture`.

---

## [6.0.0] - 2026-07-16

### Added

- Multi-provider architecture with priority-based auto-detection: GitBook, Mintlify, Docusaurus, ReadTheDocs, and generic HTML fallback.
- Per-domain storage under `~/.gitbook-downloader/docs/<domain>/`.
- Automatic snapshots before re-download, plus diff between snapshots.
- Full-text search over the library (SQLite FTS5, BM25 ranking).
- MCP server with eight async tools for AI assistants.
- JSONL export for RAG pipelines.
