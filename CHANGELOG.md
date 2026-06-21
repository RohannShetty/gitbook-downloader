# Changelog

All notable changes to GitBook Downloader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.1.0] — 2026-06-21

### Added
- **Clean package structure**: `src/gitbook_downloader/` layout ready for PyPI
- **Proper CLI**: `gitbook-dl download|split|gui` with full `--help` and argparse
- **Token-aware splitting**: Optional `tiktoken` integration for precise token counting
- **`--max-tokens` flag**: Split by token count instead of byte size
- **`pyproject.toml`**: Modern Python packaging with optional dependency groups (`[gui]`, `[tokens]`, `[all]`)
- **`CONTRIBUTING.md`**: Guidelines for contributors
- **MIT LICENSE**: Clear open-source licensing
- **`.gitignore`**: Proper exclusions for bytecode, venvs, output files

### Changed
- **No hardcoded URLs**: All paths and URLs are now configurable via CLI or GUI
- **Removed duplicate scripts**: Cleaned up old `app.py`, `download_docs.py`, `resume_download.py`, `check_pages.py`
- **Removed sample data**: Stripped `openalgo_*.md` and `openalgo_chunks/` from the repo
- **Improved README**: Comprehensive docs with quickstart, features table, and use cases
- **Renamed**: Shortcut command `gitbook-dl` → `gitbook-downloader` with alias
- **Code quality**: Separated engine/splitter/cli/gui into clean modules

### Fixed
- Folder name no longer has a space (moved from `Gitbook Downloader` to `gitbook-downloader`)
- `__pycache__` no longer tracked by git
- All lint errors resolved

---

## [3.0.0] — 2026-06-10

### Added
- **Sitemap recursion**: Now properly follows sitemap indexes (e.g., `sitemap.xml` → `sitemap-pages.xml`)
- **lxml XML parser**: Robust XML parsing with `xml.etree` fallback chain
- **Sidebar `<nav>` crawling**: Crawls GitBook sidebar for links sitemap might miss
- **Saturation detection**: Stops sidebar crawl when no new links found for 5 consecutive pages
- **Page size tracking**: Each downloaded page shows its KB size in the log
- **`_failed.json` output**: Failed pages saved for manual retry
- **Retry stat tracking**: Proper retry counter in live stats

### Fixed
- **Discovery completeness**: v3 finds 330+ pages (v2 only found ~164 due to broken sitemap handling)
- **Content extraction**: Matches proven quality — strips only `nav`, `footer`, `aside`, `script`, `style`
- **Output format**: Uses `Source:` (matching original proven format)
- **Sitemap discovery**: Tries multiple common URLs (`/sitemap.xml`, `/sitemap-index.xml`)

### Changed
- Sidebar crawling limited to 30 seed pages (prevents runaway discovery)
- Final report shows total file size in KB/MB
- XML parsing: `xml.etree` → `BeautifulSoup(lxml-xml)` → skip

---

## [2.0.0] — 2026-06-10

### Added
- **Two-phase engine**: Phase 1 discovers all URLs, Phase 2 downloads with retries
- **Parallel downloads**: Configurable 1–10 workers (default 5)
- **Retry logic**: 3 attempts with exponential backoff (1s → 3s → 8s)
- **Rate limiting handling**: HTTP 429 auto-waits with increasing delay
- **Failed page tracking**: Outputs `*_failed.json` for manual retry
- **5 live stat cards**: Discovered, Downloaded, Failed, Retries, Elapsed
- **Phase indicator**: Shows current phase (Discovery vs Download)
- **Clear log button**: One-click log clearing

### Fixed
- **CTkFont initialization**: Fonts created after Tk root (fixes crash on some systems)
- **Stat label update crash**: Direct label references instead of font inspection
- **Duplicate init lines**: Removed redundant initialization

---

## [1.0.0] — 2026-06-09

### Added
- **Dashboard GUI**: Download + Split tabs with Linear-inspired dark theme
- **Basic crawler**: Single-threaded URL discovery and download
- **Markdown splitter**: Header-boundary aware splitting (`#` headers)
- **Progress bar**: Visual progress indicator
- **Activity log**: Real-time scrolling log with color-coded messages
- **Live stats**: Discovered/Downloaded counters
- **File picker**: Browse button for split input file
- **Output folder selector**: Choose where chunks are saved

---

## Types of Changes

| Icon | Type | Description |
|------|------|-------------|
| ✨ | **Added** | New features |
| 🔧 | **Changed** | Changes in existing functionality |
| 🗑️ | **Deprecated** | Soon-to-be removed features |
| ❌ | **Removed** | Removed features |
| 🐛 | **Fixed** | Bug fixes |
| 🔒 | **Security** | Vulnerability fixes |
