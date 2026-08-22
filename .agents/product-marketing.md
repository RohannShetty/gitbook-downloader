# Product Marketing Context

**Document version:** v1
**Last updated:** 2026-08-22

## Product Overview
**One-liner:** gitbook-downloader turns any documentation website into clean, LLM-ready Markdown — one command, zero scraping code.
**What it does:** Point it at a docs URL and it detects the platform (GitBook, Mintlify, Docusaurus, ReadTheDocs, MkDocs, or any site), crawls intelligently within your scope, and writes a page tree of Markdown files plus a combined book file, an `llms.txt` manifest, and per-page frontmatter. A terminal UI, CLI, and MCP server all drive the same engine; every download lands in a searchable local library.
**Product category:** Developer tools → documentation downloaders / AI data preparation ("get docs into my LLM")
**Product type:** Free open-source (MIT), installable CLI/TUI with prebuilt binaries
**Business model:** None — OSS. Success = stars, installs, contributors.

## Target Audience
**Target companies:** Solo devs to small teams building with LLMs/RAG; AI-tooling enthusiasts; technical writers archiving docs.
**Decision-makers:** The developer themselves (self-serve, no buying process).
**Primary use case:** "Give me this entire doc site as clean Markdown so my LLM can read it without me scraping or copy-pasting."
**Jobs to be done:**
- Feed complete, accurate project documentation to an LLM/RAG pipeline in one step
- Keep an offline, versioned mirror of docs that change under them
- Search across every doc site they've ever downloaded
**Use cases:**
- Prepping context for Claude/ChatGPT/Cursor about a third-party API
- Building a RAG corpus from vendor docs
- Snapshotting docs before a vendor rewrites them

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| LLM builder | md quality, completeness, token efficiency | Scrapers break on SPAs/nav leakage; manual copying loses pages | Faithful extraction, structured output, frontmatter for chunking |
| DevOps/tooling dev | scriptability, CI use, exit codes | GUI-only tools can't automate | First-class CLI + MCP, presets, deterministic output |
| Docs archivist | fidelity, versions, diffs | Sites vanish or rewrite; wget dumps HTML garbage | Snapshots, site-version detection, clean md |

## Problems & Pain Points
**Core problem:** Documentation sites are hostile to bulk capture — JS-rendered nav, forum noise, multi-version layouts — and existing tools either dump raw HTML or miss half the pages.
**Why alternatives fall short:**
- `wget`/HTTrack: HTML soup, useless for LLMs
- Generic AI scrapers (Firecrawl et al.): per-page APIs, cost money, no local library/versioning
- One-off Python scripts: break on every provider redesign
**What it costs them:** Hours of cleanup per site; silently incomplete context → LLM answers wrong about the product.
**Emotional tension:** "I can't trust that my agent read the whole docs — did it miss the auth section?"

## Competitive Landscape
**Direct:** Crawl4AI / Scrapy recipes — powerful but require coding; no TUI/library/presets.
**Secondary:** Firecrawl / single-page-to-md APIs — hosted, metered pricing, no ownership of corpus or version history.
**Indirect:** Copy-paste into chat / vendor-provided llms.txt — only exists on well-behaved sites, no archive.
Each falls short for our user because none combine *auto-detection + clean md contract + local searchable library + snapshots* in one free tool.

## Differentiation
**Key differentiators:**
- Invisible provider intelligence — user never picks a scraper
- Four-part output contract (page tree + book file + llms.txt + frontmatter)
- Local Library: FTS5 search across every download, snapshot diffing
- MCP server: agents consume the same engine directly
**How we do it differently:** Provider-specific extractors behind one URL-in/docs-md-out interface.
**Why that's better:** Zero glue code for the user; output is immediately RAG-ready.
**Why customers choose us:** It's the shortest path from "docs URL" to "my LLM knows this product."

## Objections
| Objection | Response |
|-----------|----------|
| "Another scraper?" | Provider-aware extraction + output contract + library — scrapers give you files, we give you a corpus |
| "Why not just Firecrawl?" | Free, local, private, versioned; no per-page billing |
| "Does it work on MY docs site?" | Generic crawler fallback + diagnostics panel shows exactly how any site was interpreted |

**Anti-persona:** Teams wanting a hosted/cloud service or CMS integration; non-technical marketers.

## Switching Dynamics
**Push:** Manual scraping/copy-paste pain; LLM answers degraded by missing pages.
**Pull:** One command; free; binaries for every OS.
**Habit:** Existing scripts/wget pipelines "work well enough."
**Anxiety:** Will extraction be faithful? (Answer: frontmatter hashes + diff view make verification visible.)

## Customer Language
**How they describe the problem:**
- "the results weren't better"
- "LLM has to go through the doc website or scrape the web url"
- "wrong numbering, wrong repo state… a complete mess"
**How they describe us:**
- "intelligent enough to understand what type of website it is and do the needful"
- "the best md file so llm can read and understand the entire project"
**Words to use:** capture, docs, Markdown, LLM-ready, one command, library, snapshot, detect
**Words to avoid:** scrape (negative connotation), crawl-jargon, enterprise-speak
**Glossary:** see CONTEXT.md (Source, Provider, Site version, Snapshot, Library, Preset…)

## Brand Voice
**Tone:** Direct, plain-spoken, quietly confident — a tool that works, described in layman's language.
**Style:** Short sentences. Show the command, then the result. No hype adjectives.
**Personality:** Precise · Fast · Invisible-smart · Honest · Open-source-friendly

## Proof Points
**Metrics:** (to fill post-launch: stars, PyPI downloads, pages-captured benchmark)
**Customers:** Dogfooded by the author across real projects.
**Testimonials:** (collect after v7 launch)
**Value themes:**
| Theme | Proof |
|-------|-------|
| Completeness | Page tree mirrors site nav; duplicate elimination |
| Trustworthiness | Frontmatter content-hash per page; snapshot diff |
| Effortlessness | Auto-detection; presets; OS-specific binaries |

## Goals
**Business goal:** Become the default answer to "how do I get docs into my LLM."
**Conversion action:** Star → install (`pip install gitbook-downloader` or download binary) → first successful capture.
**Current metrics:** Pre-launch (v7 rebuild in progress).

## Changelog
*Newest first. One line per revision: what changed and why.*
- v1 (2026-08-22) — Initial context, drafted from v7 rebuild planning session.
