<div align="center">

<img src="assets/logo-icon.svg" alt="gitbook-downloader logo — a page flowing into a terminal prompt" width="96" />

# `gitbook-downloader`

**Any docs site → LLM-ready Markdown.**
One command.

[![License: MIT](https://img.shields.io/badge/license-MIT-f59e0b?style=flat-square&labelColor=18181b)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3f3f46?style=flat-square&labelColor=18181b)](pyproject.toml)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-3f3f46?style=flat-square&labelColor=18181b)](#)
<!-- PyPI placeholder until first publish; swap for the live badge below at release:
     [![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=18181b)](https://pypi.org/project/gitbook-downloader/) -->
[![PyPI](https://img.shields.io/badge/pypi-coming%20with%20v7-3f3f46?style=flat-square&labelColor=18181b)](https://pypi.org/project/gitbook-downloader/)

</div>

---

## Capture your first site in 30 seconds

```bash
pip install gitbook-downloader
```

> Not on PyPI yet — the badge above flips when v7 publishes. Until then:
>
> ```bash
> pip install git+https://github.com/RohannShetty/gitbook-downloader.git
> ```

Point it at any documentation site:

```bash
gitbook-dl capture https://docs.example.com
```

You get:

- **A page tree** — one Markdown file per page, mirroring the site's navigation, written to `docs.example.com-docs/`
- **`book.md`** — the whole site in one file with a table of contents on top, ready to paste into an LLM
- **`llms.txt`** — a manifest of everything captured, plus frontmatter on every page (source URL, title, crawl date, content hash)

Works with GitBook, Mintlify, Docusaurus, ReadTheDocs — or any site. You never pick an extractor; detection is automatic.

Every capture also lands in your local library (`~/.gitbook-downloader/`), so search, history, and diffs work across all your projects.

## What you can do with it

| | |
|---|---|
| **Point it, it detects** — GitBook, Mintlify, Docusaurus, ReadTheDocs, or any site. No config, no extractor picking. | **One output contract** — page tree + `book.md` + `llms.txt` + frontmatter with a content hash per page. Same shape every time. |
| **Local library** — every capture is indexed and searchable across all sites you've taken: `gitbook-dl search "rate limits"` | **Snapshots** — re-capture a site and the old copy is kept. `gitbook-dl diff docs.example.com 1.0.0 1.1.0` shows exactly what changed. |
| **Three ways in** — terminal UI, CLI, and an MCP server for AI agents. All three drive the same engine. | **Stays out of your way** — path scope, exclusions, and presets in `gitbook-downloader.toml`. Deterministic output you can script against. |

## The output contract

Four artifacts, every time:

```text
docs.example.com-docs/
├── pages/
│   ├── getting-started/
│   │   ├── introduction.md      ← frontmatter: url, title, date, hash
│   │   └── installation.md
│   └── api/
│       └── authentication.md
├── book.md                      ← whole site, one file, TOC on top
└── llms.txt                     ← manifest: what was captured, where
```

Feed the tree to a RAG pipeline, paste `book.md` into a chat, point an agent at `llms.txt`.

## Compare the options

Capability categories only — we don't publish benchmark numbers we haven't measured.

| | gitbook-downloader | wget | Firecrawl | Crawl4AI |
|---|---|---|---|---|
| Output | Clean Markdown + llms.txt | Raw HTML | Markdown via API | Markdown |
| Runs locally | Yes | Yes | No (hosted API) | Yes |
| Cost | Free, MIT | Free | Metered per page | Free |
| Provider auto-detect | Yes | No | No | No |
| Local searchable library | Yes | No | No | No |
| Snapshots + diff | Yes | No | No | No |
| Code required | None | None | API key | Python code |

## For AI agents (MCP)

AI agents can drive the same engine directly — no shelling out, no parsing. Install the extra (`pip install "gitbook-downloader[mcp]"`), then register the server:

```json
{
  "mcpServers": {
    "gitbook-downloader": {
      "command": "gitbook-dl",
      "args": ["mcp"]
    }
  }
}
```

## Roadmap

An item moves to "done" only when it's merged and verifiable by a user.

**Shipping in the v7 rebuild**

- Textual TUI: wizard, library browser, search, snapshot diff view, diagnostics panel
- Presets in `gitbook-downloader.toml`, actually wired into every capture
- Site-version detection (`/v1/`, `/en/latest/`) with `--latest-only` / `--versions`
- Release binaries for Windows, Linux, macOS — built automatically when we tag v7.0.0

**Later**

- More provider-specific extractors
- Resume interrupted captures
- Package-manager channels (winget, scoop, homebrew)

---

MIT © Rohan Shetty · built for people who feed docs to LLMs

Issues → [github.com/RohannShetty/gitbook-downloader/issues](https://github.com/RohannShetty/gitbook-downloader/issues)
Contributing → [CONTRIBUTING.md](CONTRIBUTING.md)
