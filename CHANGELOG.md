# Changelog

All notable changes to GitBook Downloader.

---

## [4.0.0] — 2026-06-23

### 🚀 Streaming Pipeline
- **Discover + download simultaneously** — pages start downloading as they're found, no waiting for full discovery
- 5 parallel workers by default, configurable 1–10
- Thread-safe producer/consumer architecture with proper sentinel handling

### 🔄 Incremental Updates
- **Parse existing .md file** to find already-downloaded URLs
- **Only fetch new/changed pages** — appends to your existing file
- One-click "Update" button on any past download in the dashboard
- History stored in `~/.gitbook-downloader/history.json`

### 🎨 Stripe Design System
- Complete GUI redesign using Stripe's visual language
- Clean white surface, deep navy headings (`#061b31`), purple accent (`#533afd`)
- Weight-300 typography throughout
- Blue-tinted shadows, 4px border radius
- Dashboard view with download history cards
- Auto-split prompt after every download

### 🔗 Smart URL Handling
- **Fragment deduplication** — strips `#section` anchors before download
- Verified: original 38 MB file was 92% duplicate content from fragment URLs
- New output: 673 unique pages vs 37 unique in old file (18x more content)

### 🐛 Fixed
- Deadlock in streaming pipeline when discovery finishes before downloads
- Relative import errors in PyInstaller builds
- Missing log tag configurations

---

## [3.2.0] — 2026-06-23

### Added
- Parallel downloads via ThreadPoolExecutor (configurable workers)
- Modern GUI redesign (sidebar navigation, animated stats)
- PyInstaller packaging: single 35 MB .exe
- GitHub Actions for auto-build on release tags

### Fixed
- Relative imports breaking PyInstaller executable
- Missing `--workers` flag in CLI

---

## [3.1.0] — 2026-06-21

### Added
- Clean package structure: `src/gitbook_downloader/` layout
- Proper CLI with argparse (`download`, `split`, `gui` subcommands)
- `pyproject.toml` with optional dependency groups
- MIT LICENSE, CONTRIBUTING.md, .gitignore

### Changed
- Removed hardcoded paths and URLs
- Stripped duplicate scripts and sample data
- Simplified to single BFS engine (removed over-engineered SmartEngine)

### Fixed
- Folder renamed from `Gitbook Downloader` (with space) to `gitbook-downloader`

---

## [3.0.0] — 2026-06-10

### Added
- Sitemap recursion with XML parsing
- Sidebar `<nav>` crawling for complete page discovery
- Saturation detection to stop when all pages found
- Page size tracking in download log
- Failed URL tracking (`_failed.json`)

### Fixed
- Discovery completeness: v3 finds 330+ pages vs v2's 164
- Content extraction matching proven quality

---

## [2.0.0] — 2026-06-10

### Added
- Two-phase engine: Phase 1 discovers URLs, Phase 2 downloads
- Parallel downloads with configurable workers
- Retry logic with exponential backoff (1s → 3s → 8s)
- Rate limiting handling (HTTP 429 auto-wait)
- Live stat cards: Discovered, Downloaded, Failed, Retries, Elapsed

---

## [1.0.0] — 2026-06-09

### Added
- Initial dashboard with Download + Split tabs
- Linear-inspired dark theme GUI
- Basic BFS crawler
- Markdown splitter with header-boundary awareness
- Progress bar, activity log, live stats
