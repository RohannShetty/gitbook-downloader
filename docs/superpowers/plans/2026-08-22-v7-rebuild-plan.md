# v7 Rebuild — Master Plan (single source of truth)

**Date:** 2026-08-22 · **Status:** EXECUTING · **Mode:** subagent lanes, no ticket tracker
**Inputs:** `docs/superpowers/plans/2026-08-22-docs-version-audit-findings.md`, `docs/superpowers/plans/2026-08-22-download-flow-audit-findings.md`, grilling session decisions, `.agents/product-marketing.md`, `CONTEXT.md`.

## 1. Locked decisions

| Decision | Value |
|---|---|
| Scope | Engine-keep, shell-rebuild (salvage extraction; rebuild CLI/TUI/storage around it) |
| Runtime | Python end-to-end, floor stays `>=3.10` |
| UI | Textual TUI, shadcn design language, **dark + light** themes |
| TUI surfaces at v7.0.0 | Wizard · Library · Search · Snapshot-diff · Diagnostics (ALL five) |
| Distribution | uv/pip + GitHub Actions binaries (Windows/Linux/macOS) + PyPI on tag |
| Repo | Same repo, name unchanged; history squashed ONCE at release (explicit go required) |
| Version | `7.0.0` |
| Output contract | page tree + book file + `llms.txt` + YAML frontmatter (all four) |
| Site versions | auto-detected; TUI asks via checkboxes; CLI defaults to ALL |
| Output location | BOTH: project-local `./<domain>-docs/` AND Library `~/.gitbook-downloader/`; flags opt out |
| Config | TOML presets (`gitbook-downloader.toml` project + global), flags override, **actually wired** |
| Search | SQLite FTS5 (kept) |
| MCP | first-class, same facade as TUI/CLI |
| Bare invocation | `gitbook-dl <url>` = capture (documented behavior becomes true); bare `gitbook-dl` = TUI |
| Docs | rewritten in layman language, honest claims only, zero fabricated benchmarks |

## 2. The one seam that matters + testing seams (user-approved)

1. **Facade** `api.capture(url, options) -> CaptureResult` — the ONLY entry for CLI/TUI/MCP.
2. **Output-contract writer** — filesystem assertions.
3. **Provider extractors** — pure functions, fixture HTML → markdown.
4. **TUI** — Textual pilot with fake engine injected.

All network-touching tests run against a local fixture server (`tests/fixtures/` frozen copies of real GitBook/Mintlify/Docusaurus/RTD pages). No live network in tests, ever.

### Facade contract (PINNED — lanes code against this exactly)

```python
# src/gitbook_downloader/api.py
@dataclass(frozen=True)
class CaptureOptions:
    workers: int = 8                      # parallel fetches
    max_pages: int | None = None          # None = unlimited (0 is INVALID, rejected)
    path_scope: tuple[str, ...] = ()      # URL path prefixes to include
    exclude_paths: tuple[str, ...] = ()   # path patterns to skip inside scope
    site_versions: tuple[str, ...] | None = None  # None=all detected; subset filters
    output_mode: Literal["both", "library", "local"] = "both"
    local_dir: Path | None = None         # default ./<domain>-docs/
    snapshot: bool = True                 # snapshot previous before overwrite
    timeout: float = 20.0

@dataclass(frozen=True)
class CaptureResult:
    source_url: str
    provider: str                  # gitbook|mintlify|docusaurus|readthedocs|mkdocs|generic
    site_versions_found: tuple[str, ...]
    pages_captured: int
    skipped: int                   # filtered/excluded/duplicate count
    warnings: tuple[str, ...]      # non-fatal issues surfaced to user/diagnostics
    library_path: Path | None
    local_path: Path | None
    book_file: Path | None
    manifest_file: Path | None     # llms.txt
    version_id: str | None         # snapshot id created, if snapshotting

def capture(url: str, options: CaptureOptions, *,
            progress: Callable[[ProgressEvent], None] | None = None) -> CaptureResult: ...
```

Progress events are dataclasses (kind: discovered|downloaded|failed|written, payload fields). Detection happens ONCE inside `capture` and is reported in the result — no double detection anywhere.

## 3. File ownership map (write-scope discipline)

| Lane | OWNS (may write) | MUST NOT touch |
|---|---|---|
| A engine | `providers/*.py`, `utils/discovery.py`, `utils/retry.py`, `engine.py`, `tests/test_engine_*`, `tests/fixtures/**`, `tests/conftest.py` | cli.py, storage/, mcp/, tui/, pyproject.toml |
| B shell | `api.py`(new), `output_contract.py`(new), `cli.py`, `utils/config.py`, `utils/export.py`, `storage/manager.py`, `storage/versioning.py`, `tests/test_shell_*` | providers/, engine.py, discovery, mcp/, tui/, pyproject.toml |
| C tui | `tui/**`(new pkg), `tests/test_tui_*` | everything outside tui/ except reading api.py contract |
| D pack | `mcp/server.py`, `pyproject.toml`, `uv.lock`, `.github/workflows/*`, `build_exe.py`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `tests/test_mcp_*` | engine/providers/tui sources |
| E docs | `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/**` (not plans/), archive of LAUNCH_KIT | all source |

Dependency notes: D's MCP fix calls `api.capture` per pinned contract (B lands the file). C codes against the pinned contract only. E starts after B reports final flag surface.

## 4. Fix checklist — Lane A (each item = regression test)

Blockers: gitbook.py:31-34 double-escaped regex (+ stray `\n---\n` lookaheads :24,:28) · discovery.py:126-127 request `/sitemap.xml`+`.gz` · engine.py:82 import urljoin · (MCP blocker is Lane D).
Wrong-content: soft-200 HTML-as-md hardening (content-type + structural sniff, all providers) · netloc filter on every sitemap `<loc>` · sitemap-index sub-locs never treated as pages · RTD `div.header` decompose narrowed (:141) · class-based sidebar/nav removal in body-fallback · **link rewriting pass** (absolutize relative href/src vs page URL; internal links → relative md paths) · charset correction (`resp.encoding`/apparent_encoding) · deterministic book order (discovery order, not completion) + title from entry page · ONE canonical normalize_url (strip fragment; keep query; used everywhere incl. BFS visited-set) · anchor-only links stripped pre-enqueue.
Discovery/scoping: BFS enforces exclude_paths · language filter fixes (bare zh/pt; segment-boundary prefix match; applies to BFS; empty-after-filter ⇒ empty result + warning, never unfiltered fallback) · `max_pages=None` truly unlimited · llms.txt parsing (relative links, trailing punctuation, www/non-www same-site) · namespace-flexible sitemap parse · detection hardening (on root-fetch failure try remaining providers before Generic; Mintlify signal = generator meta tag specifically; RTD signals tightened; detect once).

## 5. Build checklist — Lane B

`api.py` facade per §2 · `output_contract.py`: page-tree writer + book assembler (TOC, deterministic order) + `llms.txt` manifest + frontmatter (source_url/title/crawl_date/content_hash/site_version) · output routing both/library/local · storage: atomic writes (tmp+rename) everywhere · corrupt metadata ⇒ rebuild from disk (never reset to v1.0.0) · single snapshot point BEFORE download + per-domain lockfile · versions[] registry consistency + orphan cleanup · rollback without version inflation · config wiring: presets actually feed CaptureOptions defaults; flags override; `config init/show/path` commands · CLI surface:

```
gitbook-dl                        → TUI
gitbook-dl capture <url> [--scope P]... [--exclude P]... [--max-pages N]
              [--workers N] [--latest-only] [--versions v1,v2]
              [--output both|library|local] [-o DIR] [--no-snapshot]   (alias: dl)
gitbook-dl <url>                  → sugar for capture
gitbook-dl search QUERY [-d DOMAIN] [-l N]
gitbook-dl ls                     → library domains (alias: list)
gitbook-dl history DOMAIN · diff DOMAIN V1 V2
gitbook-dl split FILE --max-mb X [-o DIR] [-q]
gitbook-dl config [init|show|path] · mcp · tui
```

## 6. TUI spec — Lane C (@designer)

FIRST read `.agents/skills/anti-ui-slop/SKILL.md` and `.agents/skills/ui-design/SKILL.md`; apply them. Textual app in `src/gitbook_downloader/tui/`. Screens: Wizard (paste URL → provider auto-detect shown live → scope/version checkboxes → progress → summary), Library (domains, sizes, re-crawl/open), Search (FTS5, snippet preview), Diff (version picker → side-by-side), Diagnostics (why-this-provider explanation, extraction warnings from CaptureResult.warnings). Design tokens: canvas `#09090b` dark / `#fafafa` light; zinc scale; ONE accent amber `#f59e0b`; hairlines `#27272a`; Inter prose / JetBrains Mono numerals+code; tabular alignment. Dark AND light themes shipped. Fake-engine injection point for pilot tests.

## 7. Packaging — Lane D

pyproject: deps += `textual>=0.60`; add `[dev]` extra (pytest, pytest-timeout, pytest-asyncio); version → 7.0.0; drop tiktoken everywhere; requirements.txt regenerated from pyproject or deleted. uv init + lock committed. ci.yml: install `.[dev]`, run pytest for real, NO `|| echo`. build-release.yml: matrix win/linux/mac, PyInstaller console build of `gitbook-dl` (TUI entry), attach artifacts on `v*` tag; single source of truth for hidden-imports (delete duplication with build_exe.py). Docker: drop obsolete compose `version:` key + dead env var; ENTRYPOINT unchanged. mcp/server.py: delete output_file call — route through `api.capture`; remove double-snapshot/double-save.

## 8. Docs — Lane E (starts after B reports)

README: hero (badges MIT/Python3.10+/Win-Linux-macOS/PyPI-placeholder), 30-second quickstart matching REAL commands verbatim, feature grid ≤6 tiles, output-contract diagram, honest comparison table, MCP snippet. CHANGELOG: rebuilt from actual git history, honest dates, fabricated 5.0.0 date corrected, proper 7.0.0 section. CONTRIBUTING: real dev setup (uv), real test command, current architecture. LAUNCH_KIT.md → `docs/archive/LAUNCH_KIT_v4.md`. All layman-readable. Zero unverifiable claims.

## 9. Verification gates

- Per lane: lane's own new tests pass (`python -m pytest tests/<lane tests> -q`).
- Integration (orchestrator): FULL suite green — `python -m pytest tests/ -q --tb=short` (use repo venv if present); zero `import openalgo`-style violations n/a here; no file >1000 lines; `grep -r "customtkinter" src/` returns zero after TUI replaces GUI (dashboard.py deleted by B? NO — dashboard.py deletion decided: DELETE gui/dashboard.py + customtkinter extra in v7; tkinter GUI replaced by TUI. Lane D removes the extra; file removal owned by B since cli.py references it).
- Release ritual (separate explicit go): squash history → single baseline commit → tag v7.0.0 → workflows fire.

## 10. Out of scope for v7.0.0

Light-theme polish iterations beyond shipped default · package-manager channels (winget/scoop/homebrew) · resume-of-interrupted-downloads · PDF export promotion · MkDocs dedicated provider (generic covers it; revisit post-launch) · telemetry/analytics of any kind.
