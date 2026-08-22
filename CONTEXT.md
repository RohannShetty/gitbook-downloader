# CONTEXT.md — Domain Glossary

Shared vocabulary for gitbook-downloader v7. Nothing here describes implementation — only what words mean.

## Core nouns

- **Source** — a documentation website the user wants captured. Identified by its root URL.
- **Provider** — the *kind* of documentation platform a source runs on (GitBook, Mintlify, Docusaurus, ReadTheDocs, MkDocs, or Generic). Detection is automatic and invisible to the user; the user never picks a provider.
- **Page** — one unit of documentation content, rendered to exactly one Markdown file.
- **Site version** — a version published *by the doc site itself* (`/v1/`, `/v2/`, `/en/latest/`). A source may expose several. Distinct from a Snapshot.
- **Snapshot** — a dated local capture of a source from a past run. Re-crawling creates a new snapshot; old ones are kept so they can be diffed.
- **Library** — the global corpus at `~/.gitbook-downloader/` where every download is indexed and searchable across projects.
- **Project-local output** — Markdown written beside the user's code (`./<domain>-docs/`) when downloading for a specific repo. A download goes to project-local, the Library, or both.

## Output artifacts

- **Page tree** — per-page `.md` files mirroring the site's navigation structure.
- **Book file** — one combined `<site>.md` containing all pages under a table of contents, for single-paste LLM context.
- **Manifest (`llms.txt`)** — index file at the output root listing what was captured and where.
- **Frontmatter** — YAML header on every page: source URL, title, crawl date, content hash.

## Scoping

- **Path scope** — restrict a crawl to pages under given URL path prefixes (e.g. only `/api/`).
- **Exclusions** — URL path patterns to skip even inside the path scope (e.g. forum pages).

## Configuration

- **Preset** — a named entry in `gitbook-downloader.toml` bundling a source + scope + options, so one command re-crawls it. CLI flags override preset values.

## Interfaces

- **TUI** — the terminal UI (primary interface): wizard, library browser, search, snapshot diff, diagnostics.
- **CLI** — scriptable command surface (`gitbook-dl`).
- **MCP server** — machine interface exposing the same engine capabilities to AI agents.
