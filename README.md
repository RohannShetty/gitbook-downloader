# GitBook Downloader

> Download entire documentation sites — GitBook, Docusaurus, ReadTheDocs, Mintlify, or any documentation platform — and split into AI-friendly chunks.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-RohannShetty/gitbook--downloader-black.svg)](https://github.com/RohannShetty/gitbook-downloader)

## Features

- **Multi-provider auto-detection** — GitBook, Docusaurus, ReadTheDocs, Mintlify, or any HTML documentation
- **Parallel download** — configurable worker threads for fast crawling
- **Clean markdown extraction** — prefers native `.md` exports, falls back to HTML→markdown conversion
- **Per-domain storage** — organized `~/.gitbook-downloader/docs/<domain>/` structure
- **Versioning** — automatic snapshots before re-download; diff any two versions
- **Full-text search** — SQLite FTS5 with BM25 ranking
- **RAG-ready metadata** — wraps content with source/domain/chunk info for AI ingestion
- **MCP server** — exposes all tools for AI assistants (Claude Desktop, Cursor, Windsurf)
- **Desktop GUI** — optional CustomTkinter interface
- **Export formats** — Markdown, JSONL, RAG-metadata

## Quick Start

```bash
# Install
pip install gitbook-downloader

# Download a documentation site
gitbook-downloader https://docs.example.com

# Search downloaded docs
gitbook-downloader search "authentication"

# Split into AI-friendly chunks
gitbook-downloader split --input ~/.gitbook-downloader/docs/example.com/docs.md --max-mb 1.0

# View history
gitbook-downloader history

# Diff two versions
gitbook-downloader diff docs.example.com v1 v2
```

## Installation

### From PyPI (once published)

```bash
pip install gitbook-downloader
```

### From source

```bash
git clone https://github.com/RohannShetty/gitbook-downloader.git
cd gitbook-downloader
pip install -e ".[all]"
```

### Docker

```bash
docker-compose run --rm gitbook-downloader https://docs.example.com
```

## Usage

### CLI

```bash
# Basic download
gitbook-downloader download https://docs.example.com

# With options
gitbook-downloader download https://docs.example.com --max-pages 50 --workers 10

# Search downloaded content
gitbook-downloader search "rate limiting"

# List downloaded domains
gitbook-downloader list

# Show download history
gitbook-downloader history

# Diff versions
gitbook-downloader diff docs.example.com 2026-01-01 2026-07-01

# Split into chunks
gitbook-downloader split --input ~/.gitbook-downloader/docs/example.com/docs.md --max-mb 0.5
```

### Python API

```python
from gitbook_downloader import create_session, detect_provider, StorageManager, SearchIndex

# Download with progress
from gitbook_downloader.engine import stream_download

def on_progress(data):
    if data["phase"] == "downloaded":
        print(f"✅ {data['title']} ({data['size_kb']} KB)")

content = stream_download(
    "https://docs.example.com",
    max_pages=50,
    workers=5,
    progress_callback=on_progress,
)

# Search
search = SearchIndex()
results = search.search("authentication")
for r in results:
    print(f"{r['title']} (score: {r['rank']:.2f}): {r['snippet']}")
```

### MCP Server

Run the MCP server for AI assistant integration:

```bash
pip install gitbook-downloader[mcp]
gitbook-downloader mcp
```

Configure in your AI assistant's MCP settings:

```json
{
  "mcpServers": {
    "gitbook-downloader": {
      "command": "gitbook-downloader",
      "args": ["mcp"]
    }
  }
}
```

## Architecture

```
gitbook-downloader/
├── src/gitbook_downloader/
│   ├── cli.py          # CLI entry point (argparse)
│   ├── engine.py       # Download orchestrator
│   ├── splitter.py     # Markdown chunk splitter
│   ├── dashboard.py    # Desktop GUI (optional)
│   ├── utils/          # HTTP sessions, config, discovery, export
│   │   ├── retry.py      # HTTP retry with exponential backoff
│   │   ├── config.py     # TOML configuration loader
│   │   ├── discovery.py  # URL discovery (llms.txt, sitemap)
│   │   └── export.py     # RAG metadata, JSONL, PDF exports
│   ├── providers/      # Documentation platform providers
│   │   ├── base.py       # Abstract base + ProviderRegistry
│   │   ├── gitbook.py    # GitBook provider
│   │   ├── docusaurus.py # Docusaurus provider
│   │   ├── readthedocs.py# ReadTheDocs provider
│   │   ├── mintlify.py   # Mintlify provider
│   │   └── generic.py    # Generic HTML fallback
│   ├── storage/        # Per-domain storage + versioning
│   │   ├── manager.py    # StorageManager (read/write docs)
│   │   └── versioning.py # VersionManager (snapshot/diff/rollback)
│   ├── search/         # Full-text search (SQLite FTS5)
│   │   └── index.py      # SearchIndex with BM25 ranking
│   └── mcp/            # MCP server for AI assistants
│       └── server.py     # 8 async tools over stdio
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## Configuration

Config file: `~/.gitbook-downloader/config.toml`

```toml
workers = 5
timeout = 20
retry_attempts = 3
output_dir = "~/.gitbook-downloader"
max_pages = 0
prefer_md = true
use_llms_txt = true
min_content_chars = 60
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT License — see [LICENSE](LICENSE) for details.
