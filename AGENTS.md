# DocHarvest (gitbook-downloader) — AGENTS.md

> **Purpose**: AI-assistant guide for working in this codebase. Covers architecture, commands, patterns, and conventions.

---

## Quick Start

```bash
# Install (editable)
pip install -e .

# CLI entry points
gitbook-dl --help                 # main CLI
gitbook-dl capture <url>          # download a site
gitbook-dl search "query"         # search downloaded docs
gitbook-dl list                   # list library
gitbook-dl history <domain>       # snapshot history
gitbook-dl diff <domain> v1 v2    # diff versions
gitbook-dl split <file.md>        # split markdown
gitbook-dl mcp                    # start MCP server
gitbook-dl gui                    # desktop GUI
gitbook-dl tui                    # terminal UI
python -m gitbook_downloader      # same as gitbook-dl
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                             │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│   CLI       │   TUI       │   GUI       │   MCP Server          │
│  (cli.py)   │  (tui/app)  │ (gui/app)   │  (mcp/server.py)      │
└──────┬──────┴──────┬──────┴──────┬──────┴───────────┬────────────┘
       │             │             │                  │
       └─────────────┴──────┬──────┴──────────────────┘
                            ▼
              ┌─────────────────────────────┐
              │      api.py — CAPTURE       │
              │      FACADE (pinned §2)     │
              │  CaptureOptions → capture() │
              │  → CaptureResult            │
              └──────────────┬──────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  engine.py    │   │  providers/   │   │  storage/     │
│  Orchestrates │   │  (strategy    │   │  manager.py   │
│  crawl→extract│   │   pattern)    │   │  versioning.py│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ output_contract│   │   search/     │   │   utils/      │
│  .py          │   │  index.py     │   │  config.py    │
│  Writers      │   │  graph.py     │   │  retry.py     │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Data Flow**: `crawl (BFS)` → `extract (provider-specific)` → `normalize (output_contract)` → `store (storage)` → `index (search FTS5 + graph)` → `serve (CLI/TUI/GUI/MCP)`

---

## Key Modules — 1-Line Purpose

| File | Purpose |
|------|---------|
| `src/gitbook_downloader/__main__.py` | Module entry point (`python -m gitbook_downloader`) → delegates to `cli.main()` |
| `src/gitbook_downloader/cli.py` | All CLI commands (`capture`, `search`, `list`, `history`, `diff`, `split`, `config`, `mcp`, `gui`, `tui`), argparse, progress rendering |
| `src/gitbook_downloader/api.py` | **Pinned facade** — `CaptureOptions`/`CaptureResult`/`ProgressEvent` dataclasses + `capture()` orchestrates engine→storage→index |
| `src/gitbook_downloader/engine.py` | Core download logic: `_bfs_crawl()`, `stream_download()`, `download_urls()`, markdown link rewriting, language filtering |
| `src/gitbook_downloader/output_contract.py` | Writers: `write_page_tree()`, `assemble_book()`, `build_manifest()` (llms.txt), `publish()` |
| `src/gitbook_downloader/storage/manager.py` | `StorageManager`: per-domain dirs (`~/.gitbook-downloader/docs/<domain>/`), atomic writes, file locking, metadata registry |
| `src/gitbook_downloader/storage/versioning.py` | `VersionManager`: semver snapshots, rollback, diff, changelog over `docs.md` versions |
| `src/gitbook_downloader/search/index.py` | `SearchIndex`: SQLite FTS5 full-text search (`~/.gitbook-downloader/search.db`) |
| `src/gitbook_downloader/search/graph.py` | `DocGraph`: semantic concept graph (nodes: pages/headings/code/endpoints; edges: contains/links/references) |
| `src/gitbook_downloader/providers/base.py` | `Provider` ABC + `ProviderRegistry` (auto-detect by priority), URL helpers, HTML/SPA/challenge detection |
| `src/gitbook_downloader/providers/*.py` | Concrete providers: GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe, ReadTheDocs, Generic |
| `src/gitbook_downloader/splitter.py` | Header-aware markdown splitter (`split_markdown()`, `split_file()`) — never breaks mid-section/code-block |
| `src/gitbook_downloader/utils/config.py` | TOML config (global `~/.gitbook-downloader/config.toml` + project `./gitbook-downloader.toml`), presets, `CaptureOptions` builder |
| `src/gitbook_downloader/utils/retry.py` | `create_session()`: requests Session with `TimeoutHTTPAdapter`, exponential backoff, retry strategy |
| `src/gitbook_downloader/utils/discovery.py` | `discover_from_llms_txt()`, `discover_from_sitemap()`, URL normalization (re-exports from `providers.base`) |
| `src/gitbook_downloader/utils/export.py` | `wrap_with_rag_metadata()`, `export_to_jsonl()`, `export_to_pdf()` |
| `src/gitbook_downloader/mcp/server.py` | FastMCP server: tools `download_docs`, `search_docs`, `list_domains`, `get_doc`, `diff_versions`, `export_docs`, `query_doc_graph`, `get_related_concepts`; resources `docs://{domain}/book`; prompts |
| `src/gitbook_downloader/gui/app.py` | PyWebView launcher (Edge WebView2 on Windows), loads bundled `web/index.html` |
| `src/gitbook_downloader/gui/bridge.py` | `ApiBridge`: JS↔Python API (capture, search, library, versions, diff, export, provider detection) |
| `src/gitbook_downloader/tui/app.py` | Textual TUI shell: 5 tabbed surfaces (Wizard, Library, Search, Diff, Diagnostics), `EngineProtocol` seam |
| `src/gitbook_downloader/tui/engine_protocol.py` | **Pinned TUI contract**: mirrors `api.CaptureOptions`/`CaptureResult`/`ProgressEvent` + read-view types (`Detection`, `LibraryEntry`, `SearchHit`, `SnapshotInfo`, `DiffReport`, `CaptureRun`) |
| `src/gitbook_downloader/tui/screens/*.py` | TUI surfaces: `wizard.py` (capture flow), `library.py`, `search.py`, `diff.py`, `diagnostics.py` |

---

## Data Flow Details

### 1. Crawl (`engine.py`)
- `_bfs_crawl(start_url, provider, scope, exclude, max_pages)` — BFS over same-domain `<a>` links
- Respects `scope` (path prefixes to include) and `exclude` (substring patterns)
- Filters language-code path segments (e.g. `/de/`, `/fr/`) via `_LANG_CODES`
- Provider's `extract_links(html, page_url)` yields discovered URLs

### 2. Extract (Providers)
- Each provider implements `fetch(url, session)` → `PageContent(html, markdown, title, links)`
- `extract_content(html, url)`: provider-specific DOM→Markdown (readability, CSS selectors)
- `extract_links(html, url)`: provider-specific link extraction for crawling
- Auto-detection: `ProviderRegistry.detect(url, session)` fetches HTML, tries providers by `priority`

### 3. Normalize & Contract (`api.py` + `output_contract.py`)
- `normalize_engine_result()` coerces engine output → `list[CapturedPage]`
- `CaptureOptions` filters: `max_pages`, `scope`, `exclude`, `site_versions`, `render_js`
- `publish()` writes: page tree (`pages/`), combined `docs.md`, `llms.txt` manifest, search index, concept graph

### 4. Store (`storage/manager.py`)
- `StorageManager`: base dir `~/.gitbook-downloader/docs/<domain>/`
- `atomic_write_text()`: temp file + `os.replace()` for crash safety
- `DomainLock`: per-domain file lock (stale after 15 min)
- Metadata registry: `meta.json` tracks versions, snapshots, page counts

### 5. Version (`storage/versioning.py`)
- Semver snapshots: `v<major>.<minor>.<patch>.md` in `versions/`
- Next version derived from **both** registry + disk files (rebuild-safe)
- `snapshot()` → new version; `rollback(target)` → restore + safety snapshot; `diff(v1, v2)` → unified diff

### 6. Index (`search/index.py` + `search/graph.py`)
- FTS5: `pages_fts` table (page_id, url, title, content, site_version, domain)
- `SearchIndex.add_pages()`, `search()`, `get_page()`, `list_domains()`
- `DocGraph.build_from_pages()` parses markdown headings/code/endpoints → nodes + edges

### 7. Serve (CLI/TUI/GUI/MCP)
- All UIs call **only** `api.capture(CaptureOptions)` — single pinned facade
- TUI mirrors contract in `engine_protocol.py` (no direct engine imports)
- MCP exposes tools over stdio for LLMs
- GUI bridge exposes same operations to WebView JS

---

## Entry Points

| Entry | Module | Description |
|-------|--------|-------------|
| `gitbook-dl` / `python -m gitbook_downloader` | `cli.py:main()` | Main CLI dispatcher |
| `gitbook-dl capture` | `cli.py:cmd_capture()` | Download via facade |
| `gitbook-dl search` | `cli.py:cmd_search()` | FTS5 search |
| `gitbook-dl list` | `cli.py:cmd_list()` | Library domains |
| `gitbook-dl history` | `cli.py:cmd_history()` | Snapshot list |
| `gitbook-dl diff` | `cli.py:cmd_diff()` | Version diff |
| `gitbook-dl split` | `cli.py:cmd_split()` | Markdown chunker |
| `gitbook-dl config` | `cli.py:cmd_config()` | Config init/show/path |
| `gitbook-dl mcp` | `cli.py:cmd_mcp()` → `mcp/server.py:main()` | MCP stdio server |
| `gitbook-dl gui` | `cli.py:cmd_gui()` → `gui/app.py:launch_gui()` | Desktop GUI (PyWebView) |
| `gitbook-dl tui` | `cli.py:cmd_tui()` → `tui/app.py:run()` | Terminal UI (Textual) |

---

## Component Interaction Patterns

### Dependency Injection (Seams for Testing)
```python
# api.py — lazy resolvers as monkeypatch targets
def _load_stream_download(): ...      # → engine.stream_download
def _default_storage(): ...           # → StorageManager()
# Tests patch these to inject fakes
```

### Provider Strategy Pattern
```python
# providers/__init__.py
def detect_provider(url, session) -> Provider:
    return ProviderRegistry.detect(url, session)  # tries by priority

# providers/base.py
@ProviderRegistry.register
class GitBookProvider(Provider):
    priority = 10
    def fetch(self, url, session): ...
    def extract_content(self, html, url): ...
    def extract_links(self, html, url): ...
```

### Pinned Facade Contract (Plan §2)
**api.py** defines the **only** public capture interface:
```python
@dataclass(frozen=True)
class CaptureOptions:
    max_pages: int | None = None
    scope: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    site_versions: tuple[str, ...] = ()
    render: bool = False
    timeout: float = 20.0

@dataclass(frozen=True)
class CaptureResult:
    ok: bool
    domain: str
    pages: int
    bytes_written: int
    version_id: str | None
    error: str | None = None

def capture(url: str, options: CaptureOptions, progress=None) -> CaptureResult
```

**TUI mirrors this exactly** in `engine_protocol.py` — **do not edit casually**.

### Async Patterns
- **Engine**: synchronous (`requests` + `ThreadPoolExecutor` in `download_urls()`)
- **MCP**: `async def` tools (FastMCP requirement), bridges to sync `capture()` via `asyncio.to_thread()`
- **TUI**: `async/await` for UI, `run_worker()` for background capture
- **GUI**: PyWebView runs JS event loop; `ApiBridge` methods called from JS are synchronous (threaded by webview)

### State Management
| Layer | State | Mechanism |
|-------|-------|-----------|
| CLI | Stateless per-command | argparse + function args |
| TUI | `AppState` dataclass | Survives tab switches; `last_run: CaptureRun \| None` |
| GUI | `ApiBridge` instance | Singleton per window; `threading.Event` for progress |
| MCP | Module-level singletons | `_storage`, `_versioning`, `_search` (lazy init) |
| Storage | `DomainLock` + `meta.json` | File-lock + JSON registry |
| Search | SQLite WAL mode | Persistent `search.db` |

### Error Handling Conventions
1. **Provider errors**: Return `PageContent` with `error` field; engine continues crawling
2. **Engine errors**: Collected in `failed: list[tuple[url, error]]`; returned in normalized result
3. **Facade (`api.py`)**: `CaptureError` for invalid options/lock conflicts; `CaptureResult.ok=False` for runtime failures
4. **MCP tools**: Catch all exceptions → return `{"error": str(exc)}` dict
5. **TUI**: `Diagnostics` screen shows `CaptureRun` with `event_counts` + `errors: list[str]`
6. **GUI**: Bridge returns `{"success": bool, "error": str?, ...}` objects
7. **Atomic writes**: `atomic_write_text()` prevents partial files on crash

---

## Configuration System

**Precedence** (low → high):
1. `DEFAULTS` dict in `utils/config.py`
2. Global `~/.gitbook-downloader/config.toml`
3. Project `./gitbook-downloader.toml`
4. CLI args (merged in `capture_options_from_config()`)

**Sections flattened**: `defaults`, `download`, `output`, `capture` → scalar keys
**Presets**: Named groups under `[presets.<name>]` selectable via `--preset`

```toml
# Example config.toml
[defaults]
max_pages = 500
timeout = 30.0

[capture]
render = false
scope = ["/docs", "/api"]
exclude = ["changelog", "blog"]

[presets.fast]
max_pages = 100
timeout = 10.0
```

---

## Testing Conventions

- **Seams**: `_load_stream_download()`, `_default_storage()` in `api.py` are monkeypatch targets
- **TUI protocol**: `EngineProtocol` enables fake engine for screen tests
- **Provider tests**: Use `providers.base.Provider` ABC; test with captured HTML fixtures
- **Storage tests**: Use temp dirs via `StorageManager(base_dir=tmp_path)`
- **No project-wide test suite** in this repo (tests live in `.tmp_pytest/` as ad-hoc fixtures)

---

## Adding a New Provider

1. Create `src/gitbook_downloader/providers/newprovider.py`:
```python
from .base import Provider, ProviderRegistry

@ProviderRegistry.register
class NewProvider(Provider):
    name = "newprovider"
    priority = 50  # lower = tried first
    
    def fetch(self, url, session): ...
    def extract_content(self, html, url): ...
    def extract_links(self, html, url): ...
```
2. Import in `providers/__init__.py` (auto-registers via decorator)
3. Add to `__all__` and `list_providers()` output

---

## Common Tasks

| Task | Files to Touch |
|------|----------------|
| Add CLI flag | `cli.py:build_parser()`, `cmd_capture()`, `api.py:CaptureOptions` |
| Change output format | `output_contract.py:publish()`, `write_page_tree()`, `assemble_book()` |
| Modify crawl behavior | `engine.py:_bfs_crawl()`, `stream_download()` |
| Add search feature | `search/index.py:SearchIndex`, `search/graph.py:DocGraph` |
| New MCP tool | `mcp/server.py:@mcp.tool() async def new_tool(...)` |
| New TUI screen | `tui/screens/new.py` + register in `tui/app.py:SURFACES` |
| Config option | `utils/config.py:DEFAULTS`, `_CAPTURE_OPTION_KEYS`, `capture_options_from_config()` |

---

## Key Conventions

- **No I/O at import time** — lazy imports in `mcp/server.py`, `cli.py:_import_tui_run()`
- **Frozen dataclasses** for all public contracts (`CaptureOptions`, `CaptureResult`, `ProgressEvent`, TUI mirrors)
- **Single source of truth** for URL normalization: `providers.base.normalize_url()` (re-exported by `utils.discovery`)
- **Atomic file writes** everywhere (`atomic_write_text()`)
- **Graceful degradation** — missing optional deps (pywebview, textual, mcp) print friendly messages, don't crash
- **Type hints** on all public functions; `from __future__ import annotations` in every module
- **Structured logging** via `logging.getLogger(__name__)`; CLI configures console streams in `_configure_console_streams()`

---

## Directory Layout (User Data)

```
~/.gitbook-downloader/
├── config.toml              # Global config
├── search.db                # SQLite FTS5 index
├── docs/
│   └── <domain>/
│       ├── meta.json        # Registry: versions, snapshots, page count
│       ├── pages/           # Page tree: <relpath>.md + frontmatter
│       ├── docs.md          # Combined book (current version)
│       ├── llms.txt         # Manifest for LLM ingestion
│       └── versions/
│           ├── v1.0.0.md
│           ├── v1.1.0.md
│           └── ...
└── graph/                   # Concept graphs (future)
    └── <domain>.json
```

---

## Version History (Relevant)

- **v6**: Initial modular rewrite
- **v7**: Pinned facade (`api.py`), versioning, output contract, TUI protocol
- **v8**: GUI (PyWebView), MCP server, concept graph
- **v9**: Search FTS5, provider auto-detect registry
- **v10**: Config system (TOML + presets), splitter, export utilities
- **v11.0.1**: Current — modern shadcn/ui Desktop & CLI platform

---

## Debugging Tips

```bash
# Verbose capture
gitbook-dl capture <url> -v

# Dry-run provider detection
python -c "from gitbook_downloader.providers import detect_provider; from gitbook_downloader.utils import create_session; s=create_session(); p=detect_provider('<url>', s); print(p.name)"

# Inspect search DB
sqlite3 ~/.gitbook-downloader/search.db ".schema"

# View storage metadata
cat ~/.gitbook-downloader/docs/<domain>/meta.json | jq

# MCP debug (stdio)
gitbook-dl mcp  # connect via Claude Desktop / Cursor
```

---

## Anti-Patterns to Avoid

- ❌ Importing `engine.py` directly from CLI/TUI/GUI/MCP — **use `api.capture()` only**
- ❌ Mutating `CaptureOptions`/`CaptureResult` — they're `frozen=True`
- ❌ Writing files without `atomic_write_text()`
- ❌ Adding new public functions to `api.py` without updating TUI `engine_protocol.py` mirror
- ❌ Hardcoding paths — use `StorageManager` paths
- ❌ Blocking the UI thread in TUI/GUI — use workers/threads
- ❌ Skipping `DomainLock` — concurrent captures corrupt metadata
## Development Commands

```bash
# Install (editable, with optional extras)
pip install -e .                    # core
pip install -e ".[mcp]"             # MCP server
pip install -e ".[render]"          # Playwright SPA rendering
pip install -e ".[dev]"             # dev tools (pytest, etc.)
pip install -e ".[all]"             # everything

# Using uv (recommended)
uv pip install -e .
uv run gitbook-dl --help

# Build standalone executable (PyInstaller)
python build_exe.py                 # builds dist/gitbook-dl.exe (Windows)

# Build Docker image
docker build -t gitbook-downloader .
docker compose up                   # runs with docker-compose.yml

# Run CLI
gitbook-dl capture https://example.com/docs
gitbook-dl search "auth token"
gitbook-dl mcp                      # MCP server (stdio)
gitbook-dl gui                      # Desktop GUI
gitbook-dl tui                      # Terminal UI

# Run tests (ad-hoc fixtures in .tmp_pytest/)
uv run pytest                       # all tests
uv run pytest tests/test_mcp_server.py -v
uv run pytest tests/test_providers.py -v
uv run pytest -k "not slow"         # skip slow tests

# Run showcase site (Next.js)
cd docs && npm install && npm run build  # static export to docs/out/

# Generate release notes
python scripts/generate_release_notes.py --tag v11.0.1
```

---

## Code Conventions & Common Patterns

### Formatting & Naming
- **Black** formatting (line length 100) — `black src/ tests/`
- **isort** import sorting — `isort src/ tests/`
- **snake_case** for functions, variables, files
- **PascalCase** for classes, dataclasses, enums
- **UPPER_SNAKE** for constants
- **Type hints** on all public functions; `from __future__ import annotations` in every module
- **Frozen dataclasses** for all public contracts (`CaptureOptions`, `CaptureResult`, `ProgressEvent`, TUI protocol types)

### Error Handling
- **Provider layer**: Return `PageContent(error="...")`; engine continues
- **Engine layer**: Collect failures in `failed: list[tuple[url, str]]`
- **Facade (`api.py`)**: Raise `CaptureError` for invalid options/locks; return `CaptureResult(ok=False, error=...)` for runtime failures
- **MCP tools**: Catch all → return `{"error": str(exc)}` dict
- **TUI**: `CaptureRun` surfaces `errors: list[str]` + `event_counts` on Diagnostics screen
- **GUI**: `ApiBridge` returns `{"success": bool, "error": str?, ...}` objects
- **Atomic writes**: Always use `atomic_write_text()` — prevents partial files on crash

### Async Patterns
- **Engine**: Synchronous (`requests` + `ThreadPoolExecutor` in `download_urls()`)
- **MCP**: `async def` tools (FastMCP requirement); bridge to sync via `asyncio.to_thread(capture, ...)`
- **TUI**: `async/await` for UI; `self.run_worker()` for background capture
- **GUI**: PyWebView JS event loop; `ApiBridge` methods called from JS are synchronous (threaded by webview)
- **CLI**: Fully synchronous

### Dependency Injection (Seams for Testing)
```python
# api.py — lazy resolvers as monkeypatch targets
def _load_stream_download(): ...      # → engine.stream_download
def _default_storage(): ...           # → StorageManager()
# Tests: patch these to inject fakes
```

### Provider Strategy Pattern
```python
# providers/__init__.py
def detect_provider(url, session) -> Provider:
    return ProviderRegistry.detect(url, session)

# providers/base.py
@ProviderRegistry.register
class GitBookProvider(Provider):
    priority = 10
    def fetch(self, url, session): ...
    def extract_content(self, html, url): ...
    def extract_links(self, html, url): ...
```

### Pinned Facade Contract (Plan §2)
**api.py** defines the **only** public capture interface. TUI mirrors this exactly in `engine_protocol.py` — **do not edit casually**.

```python
@dataclass(frozen=True)
class CaptureOptions:
    max_pages: int | None = None
    scope: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    site_versions: tuple[str, ...] = ()
    render: bool = False
    timeout: float = 20.0

@dataclass(frozen=True)
class CaptureResult:
    ok: bool
    domain: str
    pages: int
    bytes_written: int
    version_id: str | None
    error: str | None = None

def capture(url: str, options: CaptureOptions, progress=None) -> CaptureResult
```

### State Management
| Layer | State | Mechanism |
|-------|-------|-----------|
| CLI | Stateless per-command | argparse + function args |
| TUI | `AppState` dataclass | Survives tab switches; `last_run: CaptureRun \| None` |
| GUI | `ApiBridge` instance | Singleton per window; `threading.Event` for progress |
| MCP | Module-level singletons | `_storage`, `_versioning`, `_search` (lazy init) |
| Storage | `DomainLock` + `meta.json` | File-lock + JSON registry |
| Search | SQLite WAL mode | Persistent `search.db` |

### Single Source of Truth
- URL normalization: `providers.base.normalize_url()` (re-exported by `utils.discovery`)
- Version string: `src/gitbook_downloader/__init__.py:__version__` (also in `pyproject.toml`)
- Config defaults: `utils/config.py:DEFAULTS`

### Logging
- Structured logging via `logging.getLogger(__name__)` in each module
- CLI configures console streams in `_configure_console_streams()`
- Levels: DEBUG (verbose), INFO (progress), WARNING (retries), ERROR (failures)

---

## Runtime/Tooling Preferences

| Preference | Value |
|------------|-------|
| **Runtime** | Python >= 3.10 (3.10, 3.11, 3.12, 3.13 supported) |
| **Package Manager** | **uv** (recommended) or pip |
| **Virtual Env** | `uv venv` or `python -m venv .venv` |
| **Build Tool** | `build_exe.py` (PyInstaller) for standalone; `pip wheel` for PyPI |
| **Container** | Dockerfile (multi-stage) + docker-compose.yml |
| **Type Checker** | `mypy` (not in CI yet; run manually: `mypy src/`) |
| **Linter** | `ruff` (fast) or `flake8` |
| **Formatter** | `black` + `isort` |
| **Editor** | VS Code with Python extension; `settings.json` recommends ruff, black-on-save |
| **CI** | GitHub Actions (`.github/workflows/`) — runs on push/PR |

**Required Dependencies** (in `pyproject.toml`):
- `requests>=2.28`, `beautifulsoup4>=4.11`, `markdownify>=0.11`, `lxml>=4.9`
- `textual>=0.60` (TUI), `pyperclip>=1.8`
- `pywebview>=6.2.1` (GUI — Edge WebView2 on Windows)
- `fpdf2>=2.8.8` (PDF generation)

**Optional Extras**:
- `mcp` → `mcp>=1.2.0` (MCP server)
- `render` / `js` → `playwright>=1.40` (SPA rendering)
- `dev` → `pytest>=8.0`, `pytest-timeout`, `pytest-asyncio`, `pytest-cov`

---

## Testing & QA

### Test Framework
- **pytest** with `pytest-asyncio`, `pytest-timeout`, `pytest-cov`
- **Fixtures**: `conftest.py` provides `tmp_path`, `create_session`, mock HTML fixtures
- **No project-wide test suite** in this repo — tests live as ad-hoc fixtures in `.tmp_pytest/`
- **Key test modules** (when present):
  - `tests/test_mcp_server.py` — MCP tool contracts
  - `tests/test_providers.py` — Provider extraction logic
  - `tests/test_engine_providers.py` — Engine+provider integration
  - `tests/test_storage.py` — StorageManager + VersionManager
  - `tests/test_gui_bridge.py` — ApiBridge contract
  - `tests/test_release_notes.py` — 17 tests for `generate_release_notes.py`

### Running Tests
```bash
# All tests
uv run pytest

# Specific module
uv run pytest tests/test_mcp_server.py -v
uv run pytest tests/test_providers.py -v

# Skip slow/integration
uv run pytest -m "not slow"

# With coverage
uv run pytest --cov=gitbook_downloader --cov-report=term-missing
```

### Testing Patterns
1. **Provider tests**: Use captured HTML fixtures in `tests/fixtures/` (GitBook, Mintlify, Docusaurus, RTD)
2. **Storage tests**: `StorageManager(base_dir=tmp_path)` for isolation
3. **Facade tests**: Monkeypatch `_load_stream_download()` and `_default_storage()` in `api.py`
4. **TUI tests**: Use `EngineProtocol` fake + `AppState` assertions
5. **MCP tests**: Call async tools directly with mocked dependencies

### QA Checklist Before PR
- [ ] `uv run pytest` passes (all tests green)
- [ ] `black --check src/ tests/` passes
- [ ] `isort --check src/ tests/` passes
- [ ] `ruff check src/` passes (or `mypy src/` if configured)
- [ ] `gitbook-dl capture <test-url>` works end-to-end
- [ ] `gitbook-dl mcp` starts without import errors
- [ ] Version bumped in `pyproject.toml` + `src/gitbook_downloader/__init__.py` + `CHANGELOG.md`

---

## Anti-Patterns to Avoid