# CONTEXT.md — Domain Glossary

Shared vocabulary for DocHarvest (`gitbook-downloader`) v11.0.0. Nothing here describes implementation — only what words mean.

## Core nouns

- **Source** — a documentation website the user wants captured. Identified by its root URL.
- **Provider** — the *kind* of documentation platform a source runs on (GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe, ReadTheDocs, or Generic). Detection is automatic and invisible to the user; the user never picks a provider.
- **Page** — one unit of documentation content, rendered to exactly one Markdown file.
- **Site version** — a version published *by the doc site itself* (`/v1/`, `/v2/`, `/en/latest/`). A source may expose several. Distinct from a Snapshot.
- **Snapshot** — a dated local capture of a source from a past run. Re-crawling creates a new snapshot; old ones are kept so they can be diffed.
- **Library** — the global corpus at `~/.gitbook-downloader/` where every download is indexed and searchable across projects.
- **Project-local output** — Markdown written beside the user's code (`./<domain>-docs/`) when downloading for a specific repo. A download goes to project-local, the Library, or both.

## Output artifacts

- **Page tree** — per-page `.md` files mirroring the site's navigation structure.
- **Book file** — one combined `<site>.md` containing all pages under a table of contents, for single-paste LLM context.
- **Manifest (`llms.txt`)** — standardized AI index file at the output root listing what was captured and where.
- **Frontmatter** — YAML header on every page: source URL, title, crawl date, content hash.
- **Exports** — RAG vector datasets (`.jsonl`), styled PDF handbooks (`.pdf`), and AST-split markdown chunks.

## Scoping

- **Path scope** — restrict a crawl to pages under given URL path prefixes (e.g. only `/api/`).
- **Exclusions** — URL path patterns to skip even inside the path scope (e.g. forum pages).

## Configuration

- **Preset** — a named entry in `gitbook-downloader.toml` bundling a source + scope + options, so one command re-crawls it. CLI flags override preset values.

## Interfaces

- **Desktop GUI** — React + Tailwind CSS + shadcn/ui application: Capture Studio, Document Library, live logs, in-app doc viewer, and export tools.
- **CLI** — scriptable command surface (`docharvest` / `gitbook-dl`).
- **MCP server** — FastMCP v2 machine interface exposing 10 tools, resources (`docs://`), and prompts to AI assistants and IDE harnesses over `stdio`.
- **TUI** — the terminal UI (`docharvest tui`): interactive wizard, library browser, search, snapshot diff, diagnostics.
