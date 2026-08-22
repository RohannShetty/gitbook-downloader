# Contributing to gitbook-downloader

Thanks for helping. This page gets you from clone to green tests in a few
minutes, and explains how the code is organized so your PR lands in the right
place.

## Development setup

You need **Python 3.10+**. [uv](https://docs.astral.sh/uv/) is recommended but
optional.

```bash
git clone https://github.com/RohannShetty/gitbook-downloader.git
cd gitbook-downloader

uv sync --extra dev --extra mcp
# or, without uv:
pip install -e ".[dev,mcp]"
```

Run the test suite:

```bash
python -m pytest tests -q
```

> **PowerShell note:** pass the directory (`tests`), not a glob like
> `tests/*.py` — PowerShell does not expand globs for external commands.

Tests never touch the network: crawls run against frozen fixture pages in
`tests/fixtures/`. If your change needs new fixture HTML, add it there rather
than fetching live sites in tests.

## How the code fits together

One seam matters: `src/gitbook_downloader/api.py`. The CLI, TUI, and MCP server
all call the same facade and own no download logic themselves.

```text
CLI (cli.py)  ──┐
TUI (tui/)    ──┼─→  api.capture(url, options) → CaptureResult
MCP (mcp/)    ──┘           │
                    engine.py (discover + fetch, provider-aware)
                             │
                    output_contract.py (page tree + book.md + llms.txt + frontmatter)
                             │
                    storage/ (library, snapshots) · search/ (FTS5 index)
```

| Package | What it does |
|---|---|
| `api.py` | The facade: validates options, snapshots, runs the engine, writes output, updates library + search index |
| `output_contract.py` | Turns captured pages into the four artifacts (page tree, `book.md`, `llms.txt`, frontmatter) |
| `engine.py` | Discovery (BFS + sitemaps) and parallel fetching |
| `providers/` | Per-platform extractors — GitBook, Mintlify, Docusaurus, ReadTheDocs, generic. HTML in, Markdown out |
| `storage/` | Per-domain library at `~/.gitbook-downloader/`, snapshots, diffs |
| `search/` | SQLite FTS5 index over the library |
| `tui/` | Textual app with five screens; supports a fake engine for tests |
| `mcp/` | MCP server wrapping the facade for AI agents |
| `utils/` | TOML config/presets, retry helpers, export helpers |
| `cli.py` | argparse surface (`gitbook-dl …`) |
| `splitter.py` | Splits large Markdown files into size-bounded chunks |

## Ground rules

- **Every bug fix ships with a test** that fails without the fix.
- New user-facing behavior? Update `README.md` and `CHANGELOG.md` in the same PR.
- **Claims policy:** no benchmarks, star counts, or testimonials we didn't earn.
  Capability claims only (see `docs/brand/BRAND.md`, §6).
- Keep `api.py` the only entry point — don't add download logic to CLI/TUI/MCP.
- Python ≥ 3.10, stdlib-first. Propose new dependencies in an issue before adding them.

## Sending a pull request

1. Fork and branch from `master`.
2. Make the change, with tests.
3. `python -m pytest tests -q` passes locally.
4. Open the PR with a short "what and why". Link any related issues.

Small PRs get reviewed faster than big ones.

## Good first issues

Genuinely open areas (check existing issues first):

- Resume interrupted captures
- Custom User-Agent option
- JSON output mode for scripting
- More provider-specific extractors
