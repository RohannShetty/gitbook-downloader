# Changelog

All notable changes to GitBook Downloader.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.1] — 2026-07-02

### Fixed

- **PyInstaller `--onefile` import crash** — when running the `.exe`, relative imports (`from .engine import ...`) and absolute imports (`from engine import ...`) both failed because the entry point runs standalone in a `--onefile` build. Added `sys._MEIPASS` path detection that inserts the extracted package directory into `sys.path` before any local imports are attempted. Fixes both `dashboard.py` and `cli.py`.
- **GitHub Actions workflow** — removed invalid `--collect-subpackages` flag that caused the build to fail. Now verifies EXE was produced.

### Added

- **Dark glassmorphism dashboard** — redesigned GUI with frosted-glass panels, deep space background, purple accent, rounded stat cards, real-time progress.

## [5.0.2] — 2026-07-02

### Fixed

- **Tkinter hex color crash** — removed 8-digit alpha hex colors which are unsupported by tkinter. All colors now 6-digit hex only. Fixed alpha string concatenation in Toast and split prompt.

### Added

- **Non-blocking Toast notifications** — replaced all `messagebox` modal dialogs with in-app Toast popups that auto-dismiss.

## [5.0.3] — 2026-07-02

### Added

- **`--path-scope` flag** — restricts crawling to URLs whose path starts with a given prefix (e.g., `--path-scope /docs/connect/v3/`). Prevents leeching forum, blog, changelog, and other unrelated same-domain pages.
- **Minimum content filter** — skips pages with fewer than 60 characters of real content, filtering out placeholder/empty pages.
- **MkDocs Material support** — improved HTML→markdown fallback with MkDocs Material content selectors (`md-content`, `rst-content`) and permalink anchor cleanup (`¶`). Works on non-GitBook documentation sites.

### Fixed

- **Forum/blog leeching** — the BFS crawler followed all same-domain links including forum posts, blog articles, changelogs, and unrelated product pages. Path-scoping now confines crawling to the documentation prefix.
- **Numbers not visible on MkDocs sites** — markdownify's generic `<div class="content">` selector missed MkDocs Material's content wrapper (`md-content`). Fixed by adding MkDocs-specific content selectors.

### Changed

- Engine description updated from "GitBook site" to "documentation site" — the tool now handles GitBook, MkDocs Material, Read the Docs, and generic doc sites.
- **GitHub Actions workflow** — removed invalid `--collect-subpackages` flag that caused the build to fail. Workflow now also verifies the EXE was produced.

### Added

- **Dark glassmorphism dashboard** — redesigned GUI with frosted-glass panels, deep space background (`#0d0d12`), vibrant purple accent (`#7c3aed`), rounded stat cards, real-time progress with activity log.
- **Build verification step** — GitHub Actions workflow now checks that `dist/GitBook-Downloader.exe` exists after PyInstaller completes.

---

## [5.0.0] — 2026-07-02

### Added

- **`.md`-aware content extraction** (`--prefer-md`) — downloads GitBook's native markdown export (`URL.md`) instead of converting HTML to markdown. Produces 2.2x richer content per page with proper code blocks, headers, and lists.
- **`llms.txt` discovery** (`--use-llms-txt`, on by default) — seeds the page list from GitBook's `/llms.txt` for instant complete discovery without BFS crawling startup delay.
- **Idle timeout** — producer thread stops automatically when no new pages discovered for 15 seconds and all downloads complete, eliminating indefinite crawling.
- **Agent Instructions boilerplate removal** — GitBook's AI agent instruction block is automatically stripped from `.md` export content.
- **`--no-llms-txt` and `--no-prefer-md` CLI flags** — opt-out flags for the new features.
- **Improved CLI output** — shows discovered count, errors summary, and new feature status.

### Fixed

- **`.md` URL duplication** — pages ending in `.md` are now filtered from the crawl queue. Previously, **49% of downloaded pages** were `.md` duplicates (334 out of 681 entries in a typical export). URLs ending in `.md` are now derived internally for content extraction but never crawled as separate pages.
- **Link extraction before nav stripping** — `_extract_links()` now runs on the FULL HTML before `<nav>`/`<footer>`/`<aside>` elements are removed, ensuring sidebar navigation links are discovered for crawling.
- **URL normalization** — `_norm()` strips `.md` suffixes so `URL` and `URL.md` resolve to the same normalized key, preventing duplicate detection issues.
- **Deadlock on pipeline completion** — producer now checks idle timeout and download completion before stopping, preventing indefinite hangs when all pages are downloaded but link exploration continues.
- **`urlunquote` import error on Python 3.14** — removed deprecated import.

### Performance

- **Full export (341 pages) in 7.7 seconds** — 86% faster than v4's ~2 minutes for comparable page count.
- **3.1 MB output** — compact, deduplicated, clean markdown vs v4's 5.0 MB (with 334 `.md` duplicates).
- **Zero errors** on full export of a 341-page GitBook site.

### Removed

- `<nav>` stripping before link extraction — sidebar links in CSS-classed `<div>` elements now survive extraction.

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
