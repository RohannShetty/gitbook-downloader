# README.design.md — design spec for the future `README.md`

**Status:** blueprint. Do not ship this file as the README; build `README.md` from it.
**Voice & visual rules:** see `docs/brand/BRAND.md`. Every claim below is a
capability claim — no benchmarks, star counts, or testimonials until they are real.

---

## 0. Global layout rules

- Max content width ~880 px (GitHub default). One accent color (amber `#f59e0b`),
  used at most once per screen: the license badge, the arrow in the tagline, or a
  ✓ in terminal output — never two loud ambers side by side.
- Every code block is fenced with a language tag (`bash`, `json`, `text`) so GitHub
  renders mono + copy button.
- Screenshots live in `docs/images/`; exactly one product screenshot (the TUI),
  placed after the quickstart, captioned with what it shows. No collages.
- Output-contract diagram is **ASCII in a fenced `text` block**, not mermaid:
  it renders everywhere (GitHub, PyPI, terminals, raw viewers) with zero
  dependencies and matches the hairline/mono aesthetic.

---

## 1. Hero block

```
[logo-icon inline, 20px] gitbook-downloader

Turn any documentation site into clean, LLM-ready Markdown.
One command.

<badges row>

$ pip install gitbook-downloader
```

- H1 is the package name in backticks (renders mono): `# \`gitbook-downloader\``
- One-liner, sentence case, one sentence + fragment. No adjectives beyond "clean".
- Badges row immediately under the one-liner, single line, no wrapping.

### Badge row (exact URLs, flat-square)

```markdown
[![License: MIT](https://img.shields.io/badge/license-MIT-f59e0b?style=flat-square&labelColor=18181b)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3f3f46?style=flat-square&labelColor=18181b)](pyproject.toml)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-3f3f46?style=flat-square&labelColor=18181b)](#)
[![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=18181b)](https://pypi.org/project/gitbook-downloader/)
```

**Style choice: `flat-square`, not `for-the-badge`.** `for-the-badge` is 28 px tall,
uppercase, and shouts; it fights the quiet near-black/hairline look and pushes the
quickstart below the fold. `flat-square` is compact and reads like a status row in
a well-set document. The license badge carries the single amber slot
(`-f59e0b`); everything else stays zinc on `labelColor=18181b`.
The PyPI badge is a live endpoint — it renders "not found" until first publish;
swap it in at release rather than faking a version badge now.

---

## 2. Quickstart (must fit one screen)

```bash
pip install gitbook-downloader

gitbook-dl capture https://docs.example.com
```

Then "You get:" — three bullets, verbatim contract from CONTEXT.md:

- `docs-example/` — a page tree of Markdown files mirroring the site's navigation
- `book.md` — the whole site in one file with a table of contents, for pasting into an LLM
- `llms.txt` — a manifest of everything captured, plus per-page frontmatter (source URL, title, date, content hash)

Close the section with: *"Works with GitBook, Mintlify, Docusaurus, ReadTheDocs,
MkDocs — or any site. You never pick a scraper; detection is automatic."*

Then the single TUI screenshot.

> Command note: today's CLI verb is `download` (alias `dl`) — verified against
> `src/gitbook_downloader/cli.py`. If v7 renames it to `capture`, update this line,
> the social card, and BRAND.md examples together.

---

## 3. Feature grid (6 tiles max)

Rendered as a 2-column Markdown table (3 rows). Each tile: bold name, one plain
sentence, optional micro-command. No emoji icons.

| | |
|---|---|
| **Point it, it detects** — GitBook, Mintlify, Docusaurus, ReadTheDocs, MkDocs, or any site. No config, no scraper picking. | **One output contract** — page tree + `book.md` + `llms.txt` + frontmatter with a content hash per page. Same shape every time. |
| **Local library** — every download is indexed and searchable (`gitbook-dl search "rate limits"`), across all sites you've captured. | **Snapshots** — re-crawl a site and the old capture is kept. `gitbook-dl diff` shows exactly what changed. |
| **Three ways in** — terminal UI, CLI, and an MCP server for AI agents. All three drive the same engine. | **Stays out of your way** — path scope, exclusions, and presets in `gitbook-downloader.toml`. Deterministic output you can script against. |

Every tile maps to a verified capability (CONTEXT.md + cli.py subcommands
`download/search/list/history/diff/split/config/mcp/gui`).

---

## 4. Output-contract diagram

Fenced `text` block:

```
docs-example/
├── getting-started/
│   ├── introduction.md        ← frontmatter: url, title, date, hash
│   └── installation.md
├── api/
│   └── authentication.md
├── book.md                    ← whole site, one file, TOC on top
└── llms.txt                   ← manifest: what was captured, where
```

Caption line under it: *"Four artifacts, every time. Feed the tree to a RAG
pipeline, paste `book.md` into a chat, point an agent at `llms.txt`."*

---

## 5. Comparison table

Honest capability rows only — no benchmark numbers. Columns: this tool / wget /
Firecrawl / Crawl4AI.

| | gitbook-downloader | wget | Firecrawl | Crawl4AI |
|---|---|---|---|---|
| Output | Clean Markdown + llms.txt | Raw HTML | Markdown via API | Markdown |
| Runs locally | Yes | Yes | No (hosted API) | Yes |
| Cost | Free, MIT | Free | Metered per page | Free |
| Provider auto-detect | Yes | No | No | No |
| Local searchable library | Yes | No | No | No |
| Snapshots + diff | Yes | No | No | No |
| Code required | None | None | API key | Python code |

Keep competitor descriptions factual and unflavored ("hosted, metered" — not
"overpriced"). This table states categories, not measurements.

---

## 6. MCP section

Short intro sentence: *"AI agents can drive the same engine directly — no shell-
out, no parsing."* Then the config snippet:

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

(`gitbook-dl mcp` starts the MCP server — verified in cli.py.)

---

## 7. Roadmap

Two groups, no dates we can't keep, no fake checkmarks:

**Shipping in the v7 rebuild**
- Textual TUI: wizard, library browser, snapshot diff view, diagnostics panel
- Presets in `gitbook-downloader.toml`
- Site-version detection (`/v1/`, `/en/latest/`)

**Later**
- Prebuilt binaries for Windows, Linux, macOS
- More provider-specific extractors

Rule: an item moves to "done" only when it's merged and verifiable by a user.

---

## 8. Footer

```
MIT © Rohan Shetty · built for people who feed docs to LLMs
Issues → github.com/RohannShetty/gitbook-downloader/issues
Contributing → CONTRIBUTING.md
```

No sponsor block, no star-begging, no "if this helped you buy me a coffee"
until there's a real reason to have it.

---

## Anti-pattern checklist (run before merging any README change)

- [ ] No number appears that we didn't measure ourselves
- [ ] No testimonial, real or invented
- [ ] Every command shown actually runs against current `main`
- [ ] Exactly one amber element visible per screen
- [ ] No purple/blue badges, no `for-the-badge`
- [ ] A newcomer can go top-to-bottom and finish a capture without leaving the page
