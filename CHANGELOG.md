# Changelog

## [6.0.0] - 2026-07-16

### Added
- **Multi-provider architecture** — auto-detect GitBook, Docusaurus, ReadTheDocs, Mintlify, or fallback to generic HTML
- **Provider registry** — pluggable provider system with priority-based auto-detection
- **Per-domain storage** — `~/.gitbook-downloader/docs/<domain>/` with metadata JSON
- **Version management** — automatic snapshots before re-download, diff between versions
- **Full-text search** — SQLite FTS5 with BM25 ranking, section-level indexing
- **MCP server** — 8 async tools for AI assistant integration (Claude Desktop, Cursor, etc.)
- **Progress reporting** — unified callback interface for CLI, GUI, and MCP
- **Enhanced CLI** — subcommands: download, search, list, history, diff, split, config, mcp
- **RAG-ready export** — JSONL with metadata, RAG-wrapped content
- **Docker support** — Dockerfile + docker-compose.yml

### Changed
- **Complete rewrite** of download engine to use provider/storage architecture
- **Streaming download** — real-time progress instead of blocking wait
- **Improved markdown extraction** — prefers native `.md` exports, multi-selector fallback
- **Configuration** — switched to TOML format with `~/.gitbook-downloader/config.toml`

### Removed
- Single-file `downloaded_docs.md` output (replaced by per-domain storage)

## [5.0.0] - 2025-06-01 (Initial public release)

- Initial public release
- GitBook-only downloader
- Basic markdown splitting
- ~/.gitbook-downloader/ history
