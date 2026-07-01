<div align="center">

<img src="https://img.shields.io/badge/version-5.0.0-533afd?style=for-the-badge" alt="version">
<img src="https://img.shields.io/badge/license-MIT-15be53?style=for-the-badge" alt="license">
<img src="https://img.shields.io/badge/python-3.8+-273951?style=for-the-badge" alt="python">
<img src="https://img.shields.io/badge/platform-Windows-533afd?style=for-the-badge" alt="platform">

<br><br>

<h1>⬡ GitBook Downloader</h1>

**Download entire GitBook documentation sites.**<br>
**Convert to clean markdown. Split into AI-ready chunks.**

<br>

<a href="https://github.com/RohannShetty/gitbook-downloader/releases/latest">
  <img src="https://img.shields.io/badge/Download%20.exe-Latest%20Release-533afd?style=for-the-badge&logo=windows&logoColor=white" alt="Download">
</a>

<br><br>

</div>

---

## What It Does

<table>
<tr>
<td width="65%">

```
https://docs.example.com/
        │
        ▼
  ┌─────────────┐
  │  BFS Crawler │  Finds every page
  │  5 workers   │  Parallel downloads
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  .md-aware  │  Uses GitBook's native
  │  Extraction  │  markdown export, not HTML→md
  └──────┬──────┘
         │
         ▼
    📄 docs.md
    341 pages / 3.1 MB / 0 errors
         │
         ▼
  ┌─────────────┐
  │  Splitter    │  Header-boundary chunks
  │  1 MB each   │  Never breaks code blocks
  └──────┬──────┘
         │
         ▼
  🧩 doc_part_01.md … doc_part_05.md
     Ready for ChatGPT, Claude, Gemini
```

</td>
<td width="35%">

### One command

```bash
gitbook-dl download https://docs.example.com/
gitbook-dl split downloaded_docs.md
```

### Or zero commands

Download the `.exe`, double-click, paste a URL.

### Works on any GitBook site

Docs, API references, guides, wikis — if it's on GitBook, it works.

</td>
</tr>
</table>

---

## Why Not `wget`?

| | wget | This Tool |
|---|---|---|
| **Finds all pages** | Only follows `<a href>` on visited pages | ✅ BFS crawler + `/llms.txt` discovery |
| **Clean output** | Downloads full HTML with nav, footer, scripts | ✅ Uses GitBook's native `.md` export — no HTML conversion |
| **Respects structure** | Raw dump, no organization | ✅ Each page with title + source URL + `---` separator |
| **No duplicates** | Downloads `.md` versions as separate pages | ✅ Filters `.md` URLs; normalises HTML + `.md` to same key |
| **AI-ready chunks** | No splitting | ✅ Header-boundary split, configurable size |
| **Speed** | Sequential, single-threaded | ✅ 5 parallel workers, streaming pipeline |
| **Incremental updates** | Re-downloads everything | ✅ Detects existing pages, only fetches new ones |

---

## Verified Performance (v5.0)

**Test target:** `docs.openalgo.in` — a 341-page GitBook documentation site.

| Metric | v4.0 | **v5.0** |
|---|---|---|
| Pages downloaded | 681 (incl. **334 .md dupes**) | **341** (no dupes) |
| File size | 5.0 MB | **3.1 MB** |
| Download time | ~2 minutes | **7.7 seconds** |
| Errors | Unknown | **0** |
| Parallel workers | 5 | 5 |
| Chunks produced | 5 × ~1 MB each | 5 × ~0.6 MB each |
| `.md` duplicates | 334 | **0** |
| Agent Instructions boilerplate | 333 pages | **1** (cleaned) |

---

## Installation

### Option A: Desktop App (Recommended)

1. [Download `GitBook-Downloader.exe`](https://github.com/RohannShetty/gitbook-downloader/releases/latest)
2. Double-click to launch
3. Paste a GitBook URL → Start

No Python. No terminal. No dependencies.

### Option B: Python CLI

```bash
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
```

```bash
# Download a site
gitbook-dl download https://docs.example.com/

# With custom options
gitbook-dl download https://docs.example.com/ -o mydocs.md -w 8

# Update an existing download (only new pages)
gitbook-dl download https://docs.example.com/ -o existing.md

# Split into chunks
gitbook-dl split downloaded_docs.md -s 1.0

# Launch the GUI
gitbook-dl gui
```

### CLI Reference

| Command | Flag | Default | Description |
|---|---|---|---|
| `download <url>` | | | GitBook site URL |
| | `-o, --output` | `downloaded_docs.md` | Output file |
| | `-p, --max-pages` | `0` (unlimited) | Page limit |
| | `-w, --workers` | `5` | Parallel threads |
| | `--no-llms-txt` | `True` (enabled) | Skip `/llms.txt` discovery |
| | `--no-prefer-md` | `True` (enabled) | Use HTML extraction instead of `.md` |
| `split <file>` | | | Markdown file |
| | `-o, --output-dir` | `<file>_chunks/` | Output directory |
| | `-s, --max-mb` | `1.0` | Max chunk size |
| `gui` | | | Launch desktop app |

> **New in v5.0**: `.md`-aware content extraction and `/llms.txt` discovery are enabled by default. Use `--no-llms-txt` or `--no-prefer-md` to fall back to legacy BFS-only + HTML-to-markdown mode.

---

## Real-World Use Cases

<table>
<tr>
<td width="33%">

### 🤖 Feed Docs to LLMs

Download an API reference site, split into chunks, upload to ChatGPT/Claude as knowledge files. Zero hallucinations about parameters or endpoints.

</td>
<td width="33%">

### 🔍 Build RAG Pipelines

Download documentation → split into section-aligned chunks → embed in your vector database. Each chunk is a complete, self-contained section.

</td>
<td width="33%">

### 📚 Offline Reference

Download once, read anywhere. Single searchable `.md` file. Works on flights, behind firewalls, anywhere without internet.

</td>
</tr>
</table>

---

## How It Works

### Download Engine

1. **Start at the root URL** — fetch the homepage
2. **Extract content** — remove `<nav>`, `<footer>`, `<aside>`, `<script>`, `<style>`
3. **Convert to markdown** — HTML → clean markdown via `markdownify`
4. **Discover links** — collect every internal `<a href>` on the page
5. **Stream + download** — new URLs go to a queue, worker threads download in parallel
6. **Dedup URLs** — normalize paths, strip `#fragments`, skip already-seen pages
7. **Write output** — ordered by discovery, with `Source:` attribution per page

### Splitter

1. **Read the complete `.md` file**
2. **Split on `#` headers** — each chunk starts at a markdown heading
3. **Respect size limit** — when adding a section exceeds the limit, start a new chunk
4. **Preserve structure** — code blocks, lists, tables never split mid-element
5. **Write numbered files** — `doc_part_01.md`, `doc_part_02.md`, …

---

## Architecture

```
gitbook-downloader/
├── src/gitbook_downloader/
│   ├── engine.py          Streaming BFS + parallel downloads
│   ├── splitter.py        Header-boundary chunking
│   ├── dashboard.py       Stripe-themed desktop GUI
│   └── cli.py             Terminal interface
├── .github/workflows/     Auto-build .exe on release tags
├── assets/                Social preview card
├── LAUNCH_KIT.md          Social media launch strategy
└── CHANGELOG.md           Full release history
```

---

## Contributing

Issues, PRs, and discussions welcome.

- **Bug?** [Open an issue](https://github.com/RohannShetty/gitbook-downloader/issues)
- **Feature idea?** [Start a discussion](https://github.com/RohannShetty/gitbook-downloader/discussions)
- **Want to code?** Check [open issues](https://github.com/RohannShetty/gitbook-downloader/issues) or see ideas below

### Contribution Ideas

| Difficulty | Task |
|---|---|
| 🟢 Easy | Support `GITBOOK_URL` environment variable |
| 🟢 Easy | Add `--dry-run` flag (discover only, no download) |
| 🟡 Medium | Docusaurus / ReadTheDocs / MkDocs support |
| 🟡 Medium | PDF output option |
| 🟡 Medium | Docker image |
| 🔴 Hard | Web UI (Flask / FastAPI) |
| 🔴 Hard | Scheduled downloads via cron / GitHub Actions |

---

## License

MIT © [Rohan Shetty](https://github.com/RohannShetty)

---

<div align="center">
  <sub>⬡ Built for developers who feed docs to AI. Star the repo if it helps you.</sub>
</div>
