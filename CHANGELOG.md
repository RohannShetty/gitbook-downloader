# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [11.0.4] - 2026-09-04

### 🚀 Advanced Agent MCP Suite, Granular Storage Loaders & AST-Safe Context Chunker

Version 11.0.4 modernizes the offline agent interface and documentation chunking capabilities:
- Integrates `find_docs` to resolve library/framework names to indexed domains.
- Integrates `read_doc` for AI coding agents to perform AST-safe page and topic reads with token bounding.
- Implements `extract_topic_context` in the splitter, ensuring fenced code blocks, tables, and callouts are never broken mid-element.
- Exposes `load_page` and `list_pages` on `StorageManager` for granular file access without loading monolithic documents into memory.
- Adds comprehensive TDD unit and regression test coverage.

### Added

- **`find_docs` MCP tool** (`src/gitbook_downloader/mcp/server.py`): resolves library queries and aliases (e.g. `"react"`, `"zustand"`) against local library domains and titles.
- **`read_doc` MCP tool** (`src/gitbook_downloader/mcp/server.py`): provides bounded, topic-filtered or page-level context reading for agents without truncating code fences.
- **`extract_topic_context` helper** (`src/gitbook_downloader/splitter.py`): extracts header-bounded Markdown sections and clamps to token budgets without breaking code blocks.
- **`load_page` and `list_pages`** (`src/gitbook_downloader/storage/manager.py`): allows individual page retrieval and page-tree inspection directly from `pages/`.
- **TDD Test Suite** (`tests/test_mcp_advanced_tools.py`): 4 new unit tests covering topic extraction, fence preservation, page tree loaders, and MCP tool execution.

## [11.0.3] - 2026-08-30

### 🛠️ Critical Bug Fixes, Visual Polish, Thread-Safety Hardening & Centralized Marketing Stats

Version 11.0.3 is a focused stability release: it removes 7 user-reported P0 functional bugs, hardens the GUI bridge against a Windows WebView2 race, centralizes the version constant and marketing stats, applies Direction A (Tightened dark) visual polish to the showcase, and lands 17 new regression tests. Backwards compatible with 11.0.x.

### Fixed

- **Invisible install command on showcase** (`docs/components/InstallModal.tsx`): the install panel rendered at `text-cyan/10` (effectively transparent). Bumped to `text-cyan/90` so the command is now readable.
- **PDF export toast printed `undefined`** (`frontend/src/components/DocReaderModal.tsx`): the modal read `res.file` but the Python bridge returns `res.path`. The toast now shows the real file path.
- **DiffView always showed a fake `["1.0.0"]` snapshot list**:
  - `src/gitbook_downloader/gui/bridge.py` `list_library()` now includes a real `snapshots: list[str]` field populated from `VersionManager.list_snapshots()`.
  - `frontend/src/views/DiffView.tsx` removes the hardcoded fallback and shows an empty state when no snapshots exist.
- **Capture Studio Batch tab had no Run button**: the URL queue was decorative. Added a `Run Batch` button (and a matching `Cancel Batch` button) that calls `pyApi.startCapture` once per URL sequentially, reusing the existing `ProgressEvent` pipeline.
- **CLI `--rag` and `--pdf` post-capture exports had a broken path ternary** (`src/gitbook_downloader/cli.py:215-219, 230-234`): the right-hand branch was dead because of `or result.local_path` precedence. Rewrote as straight `if exports_dir.exists(): ... else: ...` blocks.
- **Hardcoded `User-Agent: gitbook-downloader/9.0.0`** in the bridge `detect()` method: now uses `f"gitbook-downloader/{__version__}"`.
- **Stale CLI `--fast-ast` flag** (`src/gitbook_downloader/cli.py:524-525`): registered but never read, with no slow alternative. Removed from argparse entirely.
- **CommandMenu showed fake `Tab 1..Tab 6` shortcuts** that did not match the real bindings. Replaced with the real shortcuts (`Ctrl+K` command palette, `1..5` tab switch, `Ctrl+T` theme toggle, `Ctrl+R` refresh diagnostics) and added a `KEYBINDINGS` constants object.

### Changed

- **Centralized version source of truth** at `11.0.3`:
  - `src/gitbook_downloader/__version__` is the canonical source.
  - `src/gitbook_downloader/cli.py` direct-script fallback aligned.
  - `src/gitbook_downloader/gui/bridge.py` `User-Agent` and `getSystemInfo` now use the live `__version__`.
  - `frontend/src/lib/bridge.ts` `getSystemInfo` fallback aligned.
  - `README.md` version badge updated.
  - `docs/lib/version.ts` `VERSION` constant updated.
  - `frontend/index.html` GUI window title updated.
- **Centralized marketing stats** at `docs/lib/stats.ts`:
  - New `STATS` object exports `agentsShipped`, `harnesses`, `pagesCaptured`, `reductionPct`, `speedPagesPerSec`, `captureTimeSec`.
  - `Hero.tsx` (4 sites), `AgentEcosystemShowcase.tsx` (2 sites), `PersonaShowcase.tsx` (1 site), `ExportStudioPreview.tsx` (`total_pages` + `harvest_timestamp`) now read from `STATS`.
- **Defined missing `animate-fadeIn` keyframe** in `docs/app/globals.css`. The keyframe was referenced 4× in `Hero.tsx` but never defined. Existing `prefers-reduced-motion` media query still neutralizes the animation for users who request it.
- **Unified spacing scale** across the showcase: `gap-3 → gap-4`, `py-20 → py-16` (and `py-12 → py-8` where consistent). 21 substitutions across 11 components.
- **Hero direction-A polish**: dropped the two decorative radial glows, collapsed the redundant `STATUS:` / `TIME:` labels into a single dot-separated line, reduced hero gradient overlay opacity.
- **CLI command canonicalization** (`README.md`): the `docharvest capture` verb is the primary form; `crawl` is documented as a documented alias.
- **Removed dead `open_local_folder` alias** from `src/gitbook_downloader/gui/bridge.py` (never called from the TS surface, never typed in the frontend).
- **Hardened `_emit_to_js` against the Windows WebView2 message-loop race** (`src/gitbook_downloader/gui/bridge.py`): the bridge now enqueues emit calls on a `queue.Queue` consumed by a dedicated `ApiBridge.emit-drain` daemon thread. The drain thread is the only caller of `window.evaluate_js` and is started automatically by `set_window()` and stopped in `cleanup()`.
- **CLI banner dedupe**: extracted a `_banner(title, char, width)` helper that returns `(top_rule, title_line, bottom_rule)`. Replaced 8 inline `print("─" * 60)` / `print("=" * 50)` blocks across `cmd_capture`, `cmd_search`, `cmd_list`, `cmd_history`, `cmd_diff`, and `cmd_config` with `_banner()` calls.
- **Fixed `bg-border-border/60` Tailwind typo** in 8 component files (AgentEcosystemShowcase, DocTypeSelector, ExportStudioPreview, FeatureMatrix, GithubReleaseFeed, McpShowcase, OutputContract, PersonaShowcase). Now `bg-border/60` everywhere.
- **CommandMenu Global Shortcuts group**: added a new disabled `CommandGroup` documenting the 3 real global bindings (`Ctrl+K`, `Ctrl+T`, `Ctrl+R`) so the user can discover them via the in-app command palette.
- **GUI shell parity**: `frontend/src/views/CaptureStudio.tsx` spacing tokens aligned to the showcase's 4-step scale. `frontend/src/components/CommandMenu.tsx` shortcut chips use the cyan accent to match the showcase.

### Added

- **17 new regression tests** covering every P0/P1/P2 fix and every hygiene refactor. New test modules:
  - `tests/test_version_drift.py` — version constant drift across 5 files.
  - `tests/test_stats_drift.py` — STATS-only source of truth across 16 components.
  - `tests/test_install_modal_opacity.py` — install text opacity regression.
  - `tests/test_doc_reader_toast.py` — PDF toast reads `res.path`.
  - `tests/test_diff_view_snapshots.py` — DiffView + bridge `snapshots` field.
  - `tests/test_batch_run_button.py` — Batch Run + Cancel Batch buttons.
  - `tests/test_cli_rag_pdf_paths.py` — straight `if exports_dir.exists()`.
  - `tests/test_command_menu_shortcuts.py` — no fake `Tab N`, real bindings.
  - `tests/test_fast_ast_removed.py` — `--fast-ast` not in argparse / help.
  - `tests/test_visual_anchors.py` — Hero, InstallModal, Batch, DiffView anchors.
  - `tests/test_typo_classes.py` — `bg-border-border`, `text-cyan/10` banned; `animate-fadeIn` keyframe defined in `globals.css`.
  - `tests/test_bridge_contract.py` — every Python method has a TS counterpart; `list_library` includes `snapshots: list[str]`.
  - `tests/test_cli_banner.py` — `_banner()` helper used in every command.
  - `tests/test_bridge_dead_alias.py` — `open_local_folder` removed from both Python and TS sides.
  - `tests/test_bridge_thread_safety.py` — 50-burst queue dispatcher delivery + drain-thread lifecycle smoke.

### Verified

- 661/661 tests pass on Windows + Python 3.13.
- `gitbook-dl --version` reports `gitbook-downloader 11.0.3`.
- End-to-end capture: `gitbook-dl capture https://docs.readthedocs.io/en/stable/ --max-pages 3` produced a 3-page harvest with library + local outputs, banner via `_banner()` renders correctly.
- User-Agent verified at runtime: `gitbook-downloader/11.0.3`.
- Showcase builds with zero errors / zero warnings (`docs/`).
- `list_library()` returns real `snapshots: list[str]` for every domain (e.g. `["1.0.0"]` for a fresh capture, ordered newest-first).

---

## [11.0.2] - 2026-08-30

### 🎨 Showcase UI/UX Overhaul & Centralized Version Constant
Version 11.0.2 polishes the marketing showcase and tightens version-bump hygiene.

- **Showcase UI/UX overhaul & light/dark contrast fixes**:
  - `Hero`, `Header`, `Footer`, `FeatureMatrix`, `PersonaShowcase`, `InstallModal`,
    `DocTypeSelector`, `ExportStudioPreview`, `McpShowcase`, `OutputContract`,
    `FaqSection`, `AgentEcosystemShowcase`, `GithubReleaseFeed` rewritten for
    improved light/dark theme contrast and motion consistency.
- **Live GitHub release markdown parser**: `GithubReleaseFeed.tsx` now parses
    release bodies as structured markdown (headings, bullet lists, code) instead
    of plain text.
- **Centralized showcase version source of truth**:
  - Added `docs/lib/version.ts` exporting `VERSION` and `DOWNLOAD_URLS`.
  - `Hero`, `Header`, `InstallModal`, `Footer`, and `FeatureMatrix` now import
    `VERSION` instead of hardcoding `11.0.1` inline literals.
- **GUI window title**: `src/gitbook_downloader/gui/web/index.html` title
    synchronized to `DocHarvest v11.0.2`.
- **Showcase test infra scaffold (untracked, not yet active)**:
  - `docs/components/__tests__/tokens.test.tsx` will fail against the current
    showcase palette (`text-cyan-*`, `bg-zinc-*`) — design intentionally keeps
    the marketing-page palette shades. See `_tokens_codemod.mjs` for the
    planned semantic-token migration. Not wired into CI.
  - `docs/lib/github.ts` mock release data and `ExportStudioPreview.tsx`
    preview string both still cite v11.0.1 — these are snapshot fixtures
    describing historical captures, not the live version.
  - Vitest suite is not executed for this release; runtime behavior is
    covered by the existing engine/facade/TUI integration smoke checks.

---

## [11.0.1] - 2026-08-28

### 🛠️ Fixed & Improved: Playwright Error Handling, Capability Check & Badge Synchronization

- **Loud Playwright Rendering Diagnostics & Error Propagation**:
  - Fixed an issue in `engine.py` where Playwright missing errors were caught silently during `--render` mode, causing unexpected fallback to static scraping.
  - When `--render` is active and Playwright/Chromium is unavailable, the engine now immediately reports the missing dependency and provides the exact installation command.
- **Context-Aware SPA Warnings in `api.py`**:
  - Differentiated zero-page capture warnings when `--render` is active versus when static capture is attempted, preventing recursive "try --render" suggestions when `--render` was already used.
- **Dynamic Render Capability Check in Desktop GUI**:
  - Added `is_render_available` method to the PyWebView API bridge and client.
  - Toggling `Headless SPA (ON)` now verifies local Playwright availability in real time and prompts with actionable installation steps if needed.
- **Engine Badge & Version Consistency**:
  - Synchronized `CaptureStudio.tsx`, `AppSidebar.tsx`, `AboutModal.tsx`, `OnboardingTour.tsx`, and `bridge.ts` to `v11.0.1`.

---

## [11.0.0] - 2026-08-28

### 🚀 Major Architectural Rehaul: Impeccable shadcn/ui Desktop, MCP v2 Protocol, Semantic DocGraph & 8 Verified Providers

Version 11.0.0 represents a ground-up upgrade of DocHarvest:
- **Impeccable shadcn/ui Desktop GUI**:
  - React 18 + Vite 6 + Tailwind CSS desktop app with PyWebView 6 bridge.
  - Interactive **Onboarding Tour** (`OnboardingTour.tsx`) stored in persistent localStorage.
  - Full **In-App Documentation Portal** (`InAppDocsView.tsx`) covering architecture, CLI flags, and MCP setup.
  - Advanced **Markdown Viewer** (`MarkdownViewer.tsx`) featuring syntax-highlighted code blocks, Mermaid diagram rendering, dynamic Table of Contents sidebar with scrollspy, and reading time estimation.
  - Native **Headless SPA (`ON`/`OFF`)** toggle and smart detection banner with 1-click SPA mode.
- **Model Context Protocol (MCP v2) Compliance**:
  - Upgraded `gitbook_downloader.mcp.server` with 10 native tools.
  - Added **MCP Resources** (`docs://{domain}/book`, `docs://{domain}/manifest`).
  - Added **MCP Prompts** (`prompt://search-docset`, `prompt://summarize-library`).
  - Dynamic runtime compatibility for both `mcp<2` (`FastMCP`) and `mcp>=2.1` (`MCPServer`).
- **Semantic DocGraph Intelligence**:
  - Built `DocGraph` engine (`src/gitbook_downloader/search/graph.py`) for non-linear conceptual navigation (`query_doc_graph`, `get_related_concepts`).
  - Extracts page hierarchy, API endpoints, code symbols, and cross-links with minimal token consumption.
- **8 Dedicated Platform Providers**:
  - Full provider hierarchy: `GitBook` (100) → `Mintlify` (90) → `Docusaurus` (80) → `Nextra` (75) → `VitePress` (72) → `MkDocs` (70) → `ReadMe` (65) → `ReadTheDocs` (60) → `Generic` (0).
- **Loud SPA Diagnostics & Headless Rendering**:
  - Opt-in Playwright rendering (`--render`) for JavaScript-rendered SPAs (e.g. `omp.sh/docs`).
  - Upgraded wait strategy to monitor `networkidle` state and DOM text population inside `<main>` / `<article>` / `#root`.
  - Loud failure diagnostics detecting empty shells and anti-bot challenge interstitials (Cloudflare/DataDome).
- **Single-Binary Packaging Pipeline**:
  - Standardized on unified `docharvest` binaries across Windows, Linux, and macOS in `build_exe.py` and GitHub Actions.
- **14-Client IDE Integration**:
  - Verified JSON configs for Claude Code, Cursor, Windsurf, VS Code (`servers` key), Zed, JetBrains, Cline, Continue.dev, Kiro, OpenCode, Pi / Oh My Pi, Antigravity, and Codex CLI.

---

## [10.0.1] - 2026-08-23

### 🛠️ Quality & UI Polish Hotfix: Binary Naming, Project Rename & About Telemetry

Version 10.0.1 resolves key UI state discrepancies, completes the standalone executable renaming (`docharvest.exe`), adds project renaming inside the Document Library, and introduces an interactive About section with full creator attribution.

### Fixed & Improved in v10.0.1
- 🏷️ **Universal Brand & Binary Propagation**:
  - Standalone build pipeline (`build_exe.py`) updated to produce `docharvest.exe` (primary) alongside `gitbook-dl.exe` for backwards compatibility.
  - Added `docharvest` CLI command entry point in `pyproject.toml` (`[project.scripts]`).
  - Desktop GUI window title, sidebar header, and Capture Studio badges updated to `DocHarvest v10.0.1` and `v10.0 Engine`.
  - `.github/workflows/build-release.yml` now stages and publishes both `docharvest-*` and `gitbook-dl-*` cross-platform binaries.
- ⚡ **Document Library Badge Race Condition Fixed**:
  - Eliminated the tick-0 mock fallback in `frontend/src/lib/bridge.ts` that caused the count badge to flash `(1)` before the WebView2 Python bridge attached.
  - Cleaned the sidebar navigation item badge for a distraction-free library view.
- ✏️ **Project Rename Feature in Document Library**:
  - Added `StorageManager.rename_domain` and `SearchIndex.rename_domain` to safely update directory paths, metadata JSON, and SQLite FTS5 search index entries.
  - Added a **Rename (✏️)** action button on library cards and an interactive rename modal dialog in `frontend/src/views/LibraryView.tsx`.
- ❤️ **Interactive About Modal & Creator Attribution**:
  - Added `frontend/src/components/AboutModal.tsx` displaying engine specifications (AST + FastMCP + fpdf2), runtime telemetry, GitHub/Showcase links, and **"Made with ❤️ by Rohan Shetty"**.
  - Accessible via the sidebar footer heart trigger and the `Ctrl+K` command menu.

---

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
