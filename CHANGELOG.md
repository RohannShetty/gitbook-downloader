# Changelog

All notable changes to GitBook Downloader.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.0.0] — 2026-06-23

### Added

- **Streaming download pipeline** — pages download as they're discovered, no waiting for full discovery
- **Incremental updates** — parse existing `.md` file, detect already-downloaded URLs, only fetch new/changed pages
- **Download history dashboard** — past downloads shown as cards with Update, Split, and Open actions
- **Auto-split prompt** — after every download, one-click "Split into chunks" button
- **`--workers` CLI flag** — configurable parallel download threads (1–10)
- **Stripe design system** — complete GUI redesign using Stripe's visual language (white surface, navy `#061b31` headings, purple `#533afd` accent, 4px radius, blue-tinted shadows)
- **GitHub Actions CD** — auto-builds `.exe` on every release tag

### Changed

- **URL normalization** — fragments (`#section`) are now stripped before download, eliminating ~92% duplicate content vs previous versions
- **Engine architecture** — producer/consumer pattern with ThreadPoolExecutor replaces sequential BFS
- **GUI** — sidebar navigation replaced with single-page dashboard + new download view
- **History** — stored in `~/.gitbook-downloader/history.json` (auto-created)

### Fixed

- Deadlock when discovery finishes before all consumers complete
- Relative import errors in PyInstaller builds (`from .engine` → try/except fallback)
- Missing log tag configurations in dashboard

### Removed

- `max_pages` default of 500 — now defaults to 0 (unlimited)
- Sitemap-based discovery (over-engineered, BFS is more reliable)
- `tiktoken` dependency (no longer needed)

---

## [3.2.0] — 2026-06-23

### Added

- Parallel downloads via `ThreadPoolExecutor`
- Modern sidebar-based GUI redesign
- PyInstaller packaging — single `.exe` distribution
- GitHub Actions workflow for release builds
- `--workers` flag in CLI

---

## [3.1.0] — 2026-06-21

### Added

- Clean package structure (`src/gitbook_downloader/`)
- Proper CLI with argparse subcommands (`download`, `split`, `gui`)
- `pyproject.toml` with optional dependency groups (`[gui]`, `[all]`)
- MIT LICENSE
- `CONTRIBUTING.md`
- `.gitignore`

### Changed

- Removed all hardcoded paths and URLs
- Stripped duplicate scripts (`app.py`, `download_docs.py`, `resume_download.py`, `check_pages.py`)
- Removed sample data files from repository
- Simplified engine to proven BFS crawler

### Fixed

- Repository renamed from `Gitbook Downloader` (with space) to `gitbook-downloader`
- `__pycache__` no longer tracked by git

---

## [3.0.0] — 2026-06-10

### Added

- Recursive sitemap parsing with XML (`lxml` + `xml.etree` fallback)
- Sidebar `<nav>` crawling for page discovery
- Saturation detection (stops when no new links found)
- Page size tracking in download log
- Failed URL tracking via `*_failed.json`
- Retry stat tracking

### Fixed

- Discovery completeness — v3 finds 330+ pages vs v2's 164
- Content extraction quality matching proven 38 MB output
- Sitemap discovery tries multiple URLs (`/sitemap.xml`, `/sitemap-index.xml`)

---

## [2.0.0] — 2026-06-10

### Added

- Two-phase engine — Phase 1 discovers URLs, Phase 2 downloads with retries
- Parallel downloads — configurable 1–10 workers
- Retry logic — 3 attempts with exponential backoff (1s → 3s → 8s)
- HTTP 429 rate-limit handling
- Five live stat cards — Discovered, Downloaded, Failed, Retries, Elapsed
- Phase indicator (Discovery vs Download)
- Clear log button

### Fixed

- `CTkFont` initialization crash on some systems
- Stat label update crash

---

## [1.0.0] — 2026-06-09

### Added

- Initial release
- Dashboard GUI with Download + Split tabs
- Linear-inspired dark theme
- Basic BFS crawler (single-threaded, no retries)
- Markdown splitter with header-boundary awareness
- Progress bar, activity log, live stats

---

## Legend

| Icon | Type | Description |
|------|------|-------------|
| ✨ | Added | New features |
| 🔧 | Changed | Changes in existing functionality |
| 🗑️ | Deprecated | Soon-to-be removed features |
| ❌ | Removed | Removed features |
| 🐛 | Fixed | Bug fixes |
| 🔒 | Security | Vulnerability fixes |
