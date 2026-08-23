# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
