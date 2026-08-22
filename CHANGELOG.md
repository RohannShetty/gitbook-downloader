# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **About this file:** the history below was rebuilt from the actual git record
> (commit messages and tags) in August 2026, after an audit found the previous
> changelog had lost most releases and carried a fabricated date. The old file
> claimed `[5.0.0] - 2025-06-01 (Initial public release)`; both were wrong —
> the repository's first commit is dated **2026-06-21** and released **v3.1.0**.
> Dates below are commit dates from `git log`. Versions marked *(no tag)* were
> committed but never tagged, so no release artifacts were built for them.

## [Unreleased]

Everything currently on `master`, shipping next as **7.0.0** — a ground-up
rebuild of everything around the download engine.

### Added

- **Capture facade** — `gitbook_downloader.api.capture(url, options)` is now the
  single entry point shared by the CLI, TUI, and MCP server. Detection runs once;
  results come back as a typed `CaptureResult` with pages captured, skipped,
  warnings, and output paths.
- **Output contract writer** — every capture produces four artifacts: a page tree
  with YAML frontmatter (source URL, title, crawl date, SHA-256 content hash, site
  version), a combined `book.md` with a table of contents in deterministic order,
  and an `llms.txt` manifest.
- **Textual TUI** replacing the tkinter GUI — wizard, library browser, search,
  snapshot diff, and diagnostics screens, with dark and light themes.
- **TOML presets wired for real** — `[defaults]` and `[presets.<name>]` tables in
  `gitbook-downloader.toml` feed capture options; CLI flags override them;
  `gitbook-dl config init|show|path` manages the files. (v6 shipped a config file
  that nothing read.)
- **Path scoping reachable from the CLI** — `--scope` / `--exclude` flags now
  actually reach the crawler. The plumbing existed in v6 but no user-facing
  surface could set it.
- **Site-version handling** — auto-detection of `/v1/`, `/en/latest/`-style
  releases; `--latest-only` and `--versions` filters; an empty result after
  filtering stays empty with a warning instead of silently falling back to
  everything.
- **MCP server through the facade** — all eight tools route through
  `api.capture`; the `download_docs` tool crash on first call is fixed.
- **Real CI** — pytest is installed and actually run on Python 3.10/3.12 across
  Ubuntu and Windows; failures are no longer swallowed by `|| echo`.
- **Release binaries** — Windows/Linux/macOS executables built from a single
  PyInstaller spec on every `v*` tag.
- **uv** — lockfile committed for reproducible development setups.

### Changed

- Engine correctness pass: link rewriting (relative links absolutized, internal
  links point at local files), charset correction, sitemap host filtering,
  hardening against HTML-served-as-Markdown responses, one canonical URL
  normalizer, deterministic page ordering.
- Bare invocation made real: `gitbook-dl <url>` captures; bare `gitbook-dl`
  opens the TUI.
- Storage writes are atomic (temp file + rename); corrupt metadata rebuilds
  from disk instead of resetting version history.
- Snapshots are taken exactly once, before download starts, guarded by a
  per-domain lockfile.

### Removed

- The tkinter desktop GUI and its `customtkinter` dependency (replaced by the TUI).
- Dead dependencies and dead documentation — the documented TOML config now
  actually affects behavior.

## [6.0.0] - 2026-07-16 *(no tag was created)*

### Added

- Multi-provider architecture with priority-based auto-detection: GitBook,
  Mintlify, Docusaurus, ReadTheDocs, with a generic HTML fallback
- Per-domain storage under `~/.gitbook-downloader/docs/<domain>/`
- Automatic snapshots before re-download, plus diff between snapshots
- Full-text search over the library (SQLite FTS5, BM25 ranking)
- MCP server with eight async tools for AI assistants
- JSONL export for RAG pipelines
- Docker packaging (`Dockerfile`, `docker-compose.yml`)
- Streaming progress callbacks shared by CLI, GUI, and MCP

### Changed

- Download engine rewritten around the provider/storage architecture
- Configuration moved to TOML format (`~/.gitbook-downloader/config.toml`) —
  present but inert until v7 wired it into captures

### Removed

- Single-file `downloaded_docs.md` output (replaced by per-domain storage)

## [5.0.6] - 2026-07-07

### Added

- Path-scoped crawling and a minimum-content filter, so forum pages and stubs
  stop leaking into captures
- `--exclude-paths` plumbing at the provider layer *(not reachable from any user
  surface until v7)*

### Changed

- Desktop GUI redesigned ("editorial amber" palette, theme toggle)

### Fixed

- GUI path scope: Advanced panel added to the New Download card
- tkinter crash on 8-digit hex colors

## [5.0.1] - 2026-07-03

### Fixed

- PyInstaller onefile import crash in the packaged dashboard executable

## [5.0.0] - 2026-07-02 *(never tagged)*

### Added

- `.md`-aware extraction — prefers native Markdown endpoints over HTML conversion
- `llms.txt` discovery
- Duplicate elimination during crawls

### Fixed

- Deadlock when discovery finished before downloads started

## [4.0.0] - 2026-06-23

### Added

- Streaming pipeline — downloads report progress as they finish instead of
  blocking until the end

### Fixed

- PyInstaller failure caused by relative imports

## [3.2.0] - 2026-06-23

### Added

- Parallel downloads
- Modern desktop GUI
- Single `.exe` distribution

### Fixed

- Engine rewritten on a proven BFS crawler after the sitemap-based approach
  failed in practice

## [3.1.0] - 2026-06-21

### Added

- Initial public release: GitBook-only downloader, Markdown splitting,
  `~/.gitbook-downloader/` history
