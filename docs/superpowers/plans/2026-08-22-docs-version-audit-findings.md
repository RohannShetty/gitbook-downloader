# Docs / Version-Sequence / Packaging Integrity Audit — gitbook-downloader

**Date:** 2026-08-22 · **Repo:** D:\gitbook-downloader · **HEAD:** `4876043` "v6.0.0 — Multi-provider architecture, FTS5 search, MCP server, versioning" (2026-07-16)
**Scope:** research only; no code modified.

---

## Verdict

**FAIL — the docs describe a different project than the code ships.**

The version *number* is internally consistent (`6.0.0` in pyproject, `__init__.py`, cli banner, changelog), but everything around it is broken:

1. **Release process is broken**: no `v6.0.0` git tag exists, so the tag-triggered release workflow never produced artifacts.
2. **CHANGELOG.md has an impossible date** (`[5.0.0] - 2025-06-01`, ~13 months before the repo's first commit) and is missing sections for every tagged release (v3.2.0, v4.0.0, v5.0.1, v5.0.6). Commit `a46f255` "dedupe changelog" deleted history rather than merging it.
3. **README contains 3 commands that fail outright** (bare-URL invocation, `split --input` twice) plus a Python example that raises ImportError, and it documents a config file that is completely inert.
4. **CONTRIBUTING.md describes the v3.x CLI**, claims testing is manual while a pytest suite exists, and gives one broken test command.
5. **LAUNCH_KIT.md is stale v4 marketing** (wrong Python floor, removed output format, superseded GUI theme).
6. **CI never runs the tests** — pytest is never installed and the failure is swallowed by `|| echo`.
7. **The MCP server's flagship tool crashes on first use** against the current engine signature (`output_file=` kwarg doesn't exist).

---

## Version-sequence findings

| Surface | Value | Status |
|---|---|---|
| `pyproject.toml:7` | `version = "6.0.0"` | ✅ reference |
| `src/gitbook_downloader/__init__.py:3` | `__version__ = "6.0.0"` | ✅ matches |
| `src/gitbook_downloader/cli.py:251` | hardcoded `"gitbook-downloader 6.0.0"` | ⚠️ 3rd copy of the literal (drift risk) |
| `tests/test_imports.py:10` | `assert ... == "6.0.0"` | ⚠️ 4th copy of the literal |
| `CHANGELOG.md:3` | `[6.0.0] - 2026-07-16` | ✅ matches commit `4876043` date (2026-07-16) |
| `CHANGELOG.md:26` | `[5.0.0] - 2025-06-01 (Initial public release)` | ❌ impossible date + false label |
| Git tags | `v3.2.0`, `v4.0.0`, `v5.0.1`, `v5.0.6` | ❌ no `v6.0.0`, no `v5.0.0`, no `v3.1.0` |
| HEAD `4876043` | v6.0.0 commit, dated 2026-07-16, **untagged** | ❌ release workflow can't fire |
| `docker-compose.yml:5` | `image: gitbook-downloader:6.0` | ⚠️ cosmetic mismatch vs 6.0.0 |

### Tag timeline (from `git log --simplify-by-decoration`)

| Date | Ref | Commit subject |
|---|---|---|
| 2026-06-21 | *(no tag)* | 🎉 Initial release: GitBook Downloader **v3.1.0** (`6f7852d`) |
| 2026-06-23 | `v3.2.0` | feat: v3.2.0 — parallel downloads, modern GUI, single .exe (`036d53b`) |
| 2026-06-23 | `v4.0.0` | feat: v4.0.0 — streaming pipeline (`56d4aa7`) |
| 2026-07-03 | `v5.0.1` | feat: redesigned glassmorphism dashboard (`7e700a1`) |
| 2026-07-07 | `v5.0.6` | fix: GUI path-scope (`73387fe`) |
| 2026-07-16 | *(no tag — HEAD)* | v6.0.0 — Multi-provider architecture (`4876043`) |

### Sequence anomalies

1. **No `v6.0.0` tag.** `.github/workflows/build-release.yml:4-6` triggers only on `tags: v*`, so no 6.0.0 Windows release was ever built or published despite the version bump landing 5 weeks ago.
2. **Tag gap v5.0.1 → v5.0.6.** No v5.0.2–v5.0.5 tags exist, yet commit `a46f255` ("docs: dedupe changelog — clean up 5.0.1/5.0.2 sections") proves a 5.0.2 section once existed. The "dedupe" deleted changelog history instead of merging duplicates.
3. **Impossible changelog date.** `CHANGELOG.md:26` claims 5.0.0 shipped **2025-06-01** as the "Initial public release". The repo's first commit is dated **2026-06-21** and released **v3.1.0**. The entry is wrong by ~13 months and mislabels which version was first.
4. **Changelog lost every tagged release.** Sections for v3.1.0, v3.2.0, v4.0.0, v5.0.1, v5.0.6 are all absent. Commits prove they were written and later purged: `8380362`/`f4ad0a7` ("full CHANGELOG" for v4), `7255fd4` ("add v5.0.1 changelog"), `a46f255` (dedupe).
5. **Commit message vs code drift — `--exclude-paths`.** Commit `ad3efc2` says "feat: --exclude-paths flag", but `cli.py:255-259` defines the download subcommand with only `url`, `-w/--workers`, `-p/--max-pages`. The plumbing exists solely at the provider layer (`providers/base.py:65-66` and all five providers' `extract_links(..., path_scope=..., exclude_paths=...)`) plus `_bfs_crawl(engine.py:29)` — which `stream_download` calls **without** passing `path_scope` (`engine.py:227`). The feature is unreachable from any user surface.
6. **Commit message vs code drift — MkDocs.** Commit `62e4b02` claims "MkDocs support"; there is no MkDocs provider (`providers/__init__.py:22-26` registers gitbook/docusaurus/readthedocs/mintlify/generic only).
7. **Dirty working tree on top of the release commit.** Uncommitted modifications to `engine.py` (+124 lines), `providers/generic.py`, `utils/discovery.py` mean the checked-out code ≠ the v6.0.0 that docs describe.

---

## README inaccuracies

All paths relative to repo root. "Reality" = current working tree.

| # | README.md | Claim | Reality (file:line evidence) |
|---|---|---|---|
| R1 | `README.md:29` | `gitbook-downloader https://docs.example.com` (Quick Start) | **Fails.** Subcommand required; bare URL hits `args.command is None` → help + exit 1 (`src/gitbook_downloader/cli.py:305-307`). |
| R2 | `README.md:35` and `README.md:90` | `gitbook-downloader split --input <path> --max-mb 1.0` | **Fails.** No `--input` flag exists; split takes a positional `file` (`cli.py:286`). argparse rejects unknown `--input`. |
| R3 | `README.md:96` | `from gitbook_downloader import create_session, detect_provider, StorageManager, SearchIndex` | **ImportError.** `SearchIndex` is not imported/exported at top level (`src/gitbook_downloader/__init__.py:6-23`); it lives at `gitbook_downloader.search` (`search/__init__.py:3`). The documented snippet cannot run as printed. |
| R4 | `README.md:87` | `diff docs.example.com 2026-01-01 2026-07-01` | Versions are semver strings `vX.Y.Z` (`storage/versioning.py:39-64`); date strings fall through `_parse_version`'s `ValueError` → `(0,0,0)` → meaningless diff. Example identifiers match nothing. |
| R5 | `README.md:119-139` | MCP server works; configure `gitbook-downloader mcp` in Claude/Cursor | Tool count "8" is accurate, but the flagship `download_docs` tool **crashes on first call**: `mcp/server.py:136-142` passes `output_file=` which `stream_download` does not accept (`engine.py:104-111`) → `TypeError`; then treats the string return as a dict (`server.py:153-156`, `172-181` `result.get(...)`) → would also fail. |
| R6 | `README.md:174-187` | Configuration section implies `~/.gitbook-downloader/config.toml` controls behavior | Config is **inert**: `load_config()` is called only for display in `cmd_config` (`cli.py:216`); `merge_config`/`init_default_config` are never called anywhere in `src/` (grep: zero call sites); engine hardcodes `timeout=20` (`engine.py:64`), min-content 60 chars (`engine.py:242`); workers come from argparse default only (`cli.py:257`). |
| R7 | `README.md:63` | `docker-compose run --rm gitbook-downloader https://docs.example.com` | **Fails.** Compose appends the URL to `ENTRYPOINT ["gitbook-dl"]` (`Dockerfile:16`) → same bare-URL failure as R1. |
| R8 | `README.md:143-172` | Architecture tree | Omits `src/gitbook_downloader/__main__.py` and orphaned `src/launcher.py`. Otherwise accurate (all listed files exist per glob). |
| R9 | `README.md:46` | "From PyPI (once published)" | Honest caveat — fine, but note nothing in the repo publishes to PyPI (no publish workflow). |

**Verified TRUE (for balance):** multi-provider auto-detection (`providers/__init__.py:22-26`), FTS5 + BM25 ranking (`search/index.py:68` fts5 table; `ORDER BY rank` = bm25, `index.py:250-273`), snapshot-before-redownload versioning (`versioning.py:70-117`), JSONL/RAG export (`utils/export.py:52`, `:16`), optional GUI (`dashboard.py`), parallel workers (`engine.py:275`), badges consistent (LICENSE exists; GitHub URLs match `pyproject.toml:47-51`).

---

## Changelog issues

File: `CHANGELOG.md` (31 lines total).

1. **Not Keep-a-Changelog compliant** despite commit `f4ad0a7` claiming "Keep a Changelog format": no intro line, no `[Unreleased]` section, no compare-link footer, and the 5.0.0 entry uses a flat bullet list instead of Added/Changed subsections (`CHANGELOG.md:26-31`).
2. **Impossible date:** `[5.0.0] - 2025-06-01` (`CHANGELOG.md:26`) predates the repository's first commit (2026-06-21) by ~13 months.
3. **Missing versions** (tagged or committed, none documented): v3.1.0, v3.2.0, v4.0.0, v5.0.1, v5.0.2 (referenced by `a46f255`), v5.0.6.
4. **Entries vs code:**
   - `CHANGELOG.md:13` lists subcommands "download, search, list, history, diff, split, config, mcp" — omits `gui` (`cli.py:301-302`). Minor.
   - `CHANGELOG.md:11` "MCP server — 8 async tools" ✅ accurate (`mcp/server.py`: download_docs, search_docs, list_domains, get_doc, diff_versions, list_versions, export_docs, get_changelog).
   - `CHANGELOG.md:15` "Docker support" ✅ files exist — but see packaging issues (documented Docker flow broken).
   - `CHANGELOG.md:21` "switched to TOML format" ✅ file loader exists — but config is inert (R6).
   - `CHANGELOG.md:24` "Removed single-file downloaded_docs.md" ✅ consistent with per-domain storage — but LAUNCH_KIT still teaches the old flow (see below).

---

## LAUNCH_KIT.md issues (stale v4 marketing)

| # | Line | Claim | Problem |
|---|---|---|---|
| L1 | `LAUNCH_KIT.md:1` | "Launch Plan — GitBook Downloader **v4.0**" | Two major versions stale (current: 6.0.0). |
| L2 | `LAUNCH_KIT.md:88` | "Tech stack: Python **3.8+**" | `pyproject.toml:29` requires `>=3.10`. |
| L3 | `LAUNCH_KIT.md:119,215` | `gitbook-dl split downloaded_docs.md` | That output file no longer exists — v6 removed single-file output (`CHANGELOG.md:24`); storage is per-domain (`~/.gitbook-downloader/docs/<domain>/`). |
| L4 | `LAUNCH_KIT.md:135` | "Desktop GUI (**Stripe-themed**)" | GUI was redesigned to "Editorial Amber … Anti-default: no purple gradients" (`dashboard.py:1-5`; commit `fe2ce26`). |
| L5 | `LAUNCH_KIT.md:74,136` | "Updates incrementally — only fetches new pages" | False for v6: `stream_download` re-downloads every discovered URL each run (`engine.py:220-231`); there is no skip-existing logic anywhere. Only snapshotting of the previous version exists (`engine.py:308-320`). |
| L6 | `LAUNCH_KIT.md:328-331` | "What's Next: Docusaurus, ReadTheDocs, MkDocs support… Docker image" | Docusaurus, ReadTheDocs and Docker already shipped; MkDocs was claimed in commit `62e4b02` but does not exist in code. |
| L7 | `LAUNCH_KIT.md:56,78,132,185,317` | "673 pages → 5 MB → 5 chunks", "38 MB wget garbage" | Unverifiable anecdotes presented as benchmarks; also measured against the retired v4 architecture, not the v6 provider/storage rewrite. Flag as marketing, not fact. |
| L8 | `LAUNCH_KIT.md:13` | `assets/social-preview.html` | ✅ Valid — file exists and is tracked (`git ls-files assets` → `assets/social-preview.html`). |

---

## CONTRIBUTING.md issues

| # | Location | Claim | Problem |
|---|---|---|---|
| C1 | `CONTRIBUTING.md:70-82` | Project structure shows 5 modules | Stale v3 layout: omits `providers/`, `storage/`, `search/`, `mcp/`, `utils/` packages that now contain most of the code. |
| C2 | `CONTRIBUTING.md:77` | "cli.py — argparse with download/split/gui subcommands" | Actually **nine** subcommands: download, search, list, history, diff, split, config, mcp, gui (`cli.py:255-302`). |
| C3 | `CONTRIBUTING.md:89` | splitter depends on "tiktoken (optional)" | `tiktoken` appears nowhere in `src/` (git grep: zero hits). Dead claim — yet requirements.txt installs it (P2). |
| C4 | `CONTRIBUTING.md:141` | "Currently, testing is manual." | False: `tests/` contains 8 files (`test_imports.py`, `test_utils.py`, `test_storage.py`, `test_splitter.py`, `test_search.py`, `test_providers.py`, `conftest.py`, `__init__.py`) including a full smoke suite. No pytest instructions are given anywhere, and pytest isn't declared in any extra. |
| C5 | `CONTRIBUTING.md:147` | `gitbook-dl download https://docs.example.com/ -p 10 -w 2 -o test_output.md` | **Broken command**: `-o` does not exist on the download subcommand (`cli.py:255-259`). |
| C6 | `CONTRIBUTING.md:160` | `gitbook-dl split test.md -s 0.001` | ✅ Valid (`cli.py:288`). |
| C7 | `CONTRIBUTING.md:166` | `gitbook-dl gui` | ✅ Valid (`cli.py:301`). |
| C8 | `CONTRIBUTING.md:176-187` | Feature-ideas table offers "Support for Docusaurus / ReadTheDocs / MkDocs" (🔴 Hard) and "Docker image" as up-for-grabs | Docusaurus + ReadTheDocs are implemented (`providers/docusaurus.py`, `providers/readthedocs.py`); Docker exists (`Dockerfile`, `docker-compose.yml`). `--quiet` partially exists (`-q` on split, `cli.py:289`). Genuinely open: resume downloads, custom User-Agent, JSON output, web UI. |
| C9 | `CONTRIBUTING.md:131` | `python -m py_compile src/gitbook_downloader/*.py` | Glob misses all subpackages (`providers/`, `storage/`, `utils/`, `search/`, `mcp/`) — checks ~half the codebase. |

---

## Packaging issues

### P1 — CI never runs the tests (`​.github/workflows/ci.yml`)
- `ci.yml:26-29` installs only `pip install -e ".[all]"` — **pytest is never installed** (no `test`/`dev` extra exists in `pyproject.toml:37-41`).
- `ci.yml:46-48` runs `python -m pytest tests/ -v --timeout=60 || echo "No tests directory or pytest not configured"`. Without pytest installed, `python -m pytest` fails instantly and the `|| echo` swallows it → **job goes green having executed zero tests**. (`--timeout` would also need `pytest-timeout`, which isn't installed either.)
- Net effect: the "Run unit tests" step is decorative.

### P2 — Dependency drift: `requirements.txt` vs `pyproject.toml`
- `requirements.txt` includes `customtkinter>=5.2.0` — optional `[gui]` extra in `pyproject.toml:38`.
- `requirements.txt` includes `tiktoken>=0.5.0; python_version >= "3.8"` — **absent from pyproject entirely and unused by any source file** (dead dependency), with a stale `3.8` marker contradicting `requires-python >= 3.10` (`pyproject.toml:29`).
- Two sources of truth that disagree; anything installing from requirements.txt gets a different dependency set than `pip install .`.

### P3 — Release pipeline disconnected from reality
- `build-release.yml:4-6` triggers on `v*` tags; **no v6.0.0 tag exists** → no release artifact for the current version.
- `build-release.yml:27-44` hand-duplicates `build_exe.py:16-32` with diverging hidden-import lists (workflow adds `queue`, `threading`, `concurrent.futures`, `collections`, `re`; script doesn't) — two PyInstaller configs drifting apart.

### P4 — docker-compose.yml
- `docker-compose.yml:1` — `version: "3.9"` is obsolete under Compose v2 (warning noise).
- `docker-compose.yml:13` — `GITBOOK_DOWNLOADER_CONFIG=/root/.gitbook-downloader/config.toml` is read by **nothing**: there are zero `os.environ`/`getenv` references in `src/` or `tests/` (grep). Dead env var.
- `docker-compose.yml:5` — image tag `:6.0` vs actual `6.0.0` (cosmetic).
- Combined with R7/R1: the only documented way to use the image (`README.md:63`) exits with an argparse error.

### P5 — Dockerfile
- `Dockerfile:13` — editable install (`pip install -e ".[all]"`) inside an image is unconventional but functional; `ENTRYPOINT ["gitbook-dl"]` correctly matches `pyproject.toml:45`. Base `python:3.12-slim` satisfies `requires-python >=3.10`. lxml system deps (`Dockerfile:6-8`) are correct. No blocking defects beyond the compose/README flow above.

### P6 — build_exe.py / launcher
- `build_exe.py:31` builds from `src/gitbook_downloader/dashboard.py` — consistent with the workflow; `dashboard.py:11-14` contains the `sys._MEIPASS` path fix promised by commit `7587e24`. ✅
- `src/launcher.py` is **orphaned**: referenced by neither `build_exe.py` nor any workflow nor any doc.

### P7 — Empty extras advertised in error messages
- `mcp/server.py:211` tells users to `pip install 'gitbook-downloader[search]'`, but `pyproject.toml:40` defines `search = []` (empty placeholder) — the advice installs nothing.

---

## Undocumented surface area

### CLI flags/subcommands missing from README
- `search -d/--domain`, `-l/--limit` (`cli.py:264-265`)
- `diff -v/--verbose` (`cli.py:281`)
- `split -o/--output-dir`, `-q/--quiet` (`cli.py:287-289`)
- Aliases: `dl`, `ls`, `hist` (`cli.py:255,269,273`)
- `config` and `gui` subcommands get no usage examples (`cli.py:293-302`)

### Env vars
- **None are supported.** Zero `os.environ`/`getenv` in `src/` — so docker-compose's `GITBOOK_DOWNLOADER_CONFIG` is fictional, and CONTRIBUTING's idea-listing of `GITBOOK_URL` is accurately still an idea.

### Code features with no documentation anywhere
- `VersionManager.rollback()` (`storage/versioning.py:198`) — implemented, exposed via neither CLI nor MCP nor docs.
- `export_to_pdf()` (`utils/export.py:106`) — PDF/HTML-fallback export; not in README features or CLI.
- `SearchIndex.index_domain_from_storage()`, `.list_indexed_domains()`, `.get_stats()` (`search/index.py:159,294,328`) — public API with no docs.
- `path_scope` / `exclude_paths` provider parameters (`providers/base.py:65-66`) — plumbed through all five providers but unreachable from CLI/engine (see anomaly #5).
- `merge_config()` / `init_default_config()` (`utils/config.py:118,139`) — exported public API, zero call sites; there is no command to bootstrap the config file README documents.
- `StorageManager.save_chunks/delete_domain/get_total_size` (`storage/manager.py:272,291,254`) — no CLI/MCP surface.

### MCP docs vs reality
- README documents the server launch + tool count only; no per-tool reference exists. Of the 8 tools, `download_docs` is currently broken against `engine.stream_download`'s real signature (R5); the other 7 match their implementations.

---

## Suggested fix order (for the orchestrator; not applied)

1. Tag `v6.0.0` (or re-version) so the release workflow can fire; decide what the uncommitted engine/generic/discovery changes belong to.
2. Rebuild CHANGELOG from git history (restore purged v3.x/v4/v5.0.x sections; fix the fabricated 5.0.0 date).
3. Fix README Quick Start (subcommand form, positional `split` arg, correct SearchIndex import, semver diff example) and either wire config.toml into `stream_download` or stop documenting it as effective.
4. Fix `mcp/server.py` `download_docs` ↔ `stream_download` signature mismatch (broken headline feature).
5. Install pytest (+pytest-timeout) in ci.yml and drop the `|| echo`; add a `dev` extra.
6. Regenerate requirements.txt from pyproject (drop tiktoken or actually use it); delete dead `GITBOOK_DOWNLOADER_CONFIG` env var or implement it.
7. Rewrite CONTRIBUTING structure/testing sections; archive or update LAUNCH_KIT to v6 facts.
