export interface DocFramework {
  id: string
  name: string
  badge: string
  color: string
  sampleUrl: string
  heuristicMatch: string
  detectionPriority: number
  description: string
  features: string[]
  rawHtmlSnippet: string
  cleanMarkdownSnippet: string
}

export const DOC_FRAMEWORKS: DocFramework[] = [
  {
    id: "gitbook",
    name: "GitBook",
    badge: "Native Space Indexer",
    color: "from-blue-500/20 to-cyan-500/20 border-cyan-500/30 text-cyan-400",
    sampleUrl: "https://docs.openalgo.in/v/v2.0/api-reference",
    heuristicMatch: "space_id detection + /v/ version dropdowns + direct .md endpoint probe",
    detectionPriority: 100,
    description: "Deep GitBook spaces integration. Traverses multi-version dropdowns, parses space manifest JSON, and probes raw .md endpoints to fetch author-original markdown.",
    features: [
      "Direct .md raw endpoint probing bypassing HTML conversion",
      "Multi-version space selector traversal (/v/v2.0/, /v/latest)",
      "Preserves embedded code block tabs and parameter tables",
      "Automatic TOC generation from summary tree structure"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (42.8 KB HTML Soup) -->
<div class="gitbook-root-container" data-space="sp_987x">
  <nav class="sidebar-nav-sticky-top"><div class="cookie-banner-wrap">...</div>
  <ul class="nav-tree-level-1"><li class="active"><a href="/v/v2.0/auth">OAuth</a></li>...</ul>
  <main class="page-content-wrapper">
    <div class="header-anchor-wrap"><h1 id="oauth2">OAuth 2.0 Auth<a class="anchor" href="#oauth2">¶</a></h1></div>
    <div class="alert alert-warning"><svg class="icon">...</svg><span>Token expires in 3600s</span></div>
    <div class="code-block-container" data-lang="python">
      <div class="code-header"><span class="lang-label">Python</span><button class="copy-btn">Copy</button></div>
      <pre><code><span class="token-keyword">import</span> <span class="token-variable">requests</span>...</code></pre>
    </div>
  </main>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://docs.openalgo.in/v/v2.0/api-reference/oauth
title: "OAuth 2.0 Authentication"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
site_version: "v2.0"
---

# OAuth 2.0 Authentication

> ⚠️ **Warning:** Access tokens expire after 3600 seconds. Refresh via \`/oauth/v2/token\`.

## Request Signature

\`\`\`python
import requests

response = requests.post(
    "https://api.openalgo.in/v2/oauth/token",
    headers={"Authorization": "Bearer SEC_TOKEN_KEY"},
    json={"grant_type": "client_credentials"}
)
tokens = response.json()
\`\`\``
  },
  {
    id: "mintlify",
    name: "Mintlify",
    badge: "MDX & OpenAPI Extractor",
    color: "from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400",
    sampleUrl: "https://mintlify.com/docs/api-reference/overview",
    heuristicMatch: "mintlify-dom + __NEXT_DATA__ inspection + direct .md endpoint probe",
    detectionPriority: 90,
    description: "Extracts modern Mintlify documentation portals. Resolves interactive OpenAPI schemas, multi-language code snippets, and custom MDX callout tags cleanly.",
    features: [
      "Direct .md endpoint discovery for pristine source capture",
      "Multi-tab codegroup extraction (Python, JS, cURL, Go)",
      "Normalizes interactive API playground parameters into clean tables",
      "Strips Next.js client-side hydrate scripts and search modals"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (64.1 KB HTML Soup) -->
<div id="__next"><div class="mint-layout"><header class="sticky top-0 bg-background/80">...</header>
<div class="mdx-content prose prose-zinc dark:prose-invert">
  <div class="callout callout-info border-l-4 border-cyan-500">
    <div class="callout-title">Rate Limits</div>
    <div class="callout-body">Standard tier allows 100 req/min.</div>
  </div>
  <div class="tabs-container" data-tabs="python,typescript,curl">...</div>
</div></div></div>`,
    cleanMarkdownSnippet: `---
source_url: https://mintlify.com/docs/api-reference/overview
title: "API Overview & Rate Limits"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-4a5f6e7d8c9b0a1f2e3d4c5b6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b"
site_version: "latest"
---

# API Overview & Rate Limits

:::info Rate Limits
Standard tier allows 100 requests per minute per IP.
:::

## Multi-Language Quickstart

\`\`\`typescript
import { MintClient } from '@mintlify/sdk';
const client = new MintClient({ apiKey: process.env.API_KEY });
const docs = await client.documents.list();
\`\`\``
  },
  {
    id: "docusaurus",
    name: "Docusaurus",
    badge: "Versioned Sidebar Parser",
    color: "from-green-500/20 to-emerald-500/20 border-green-500/30 text-green-400",
    sampleUrl: "https://docusaurus.io/docs/advanced/routing",
    heuristicMatch: "meta[name='generator'][content*='Docusaurus'] + __docusaurus manifest",
    detectionPriority: 80,
    description: "Full Docusaurus 2 & 3 support. Scopes crawlers to exact documentation subpaths, captures version dropdowns, and transforms Docusaurus admonitions into markdown.",
    features: [
      "Version-scoped sidebar traversal (/docs/next/, /docs/1.0.0/)",
      "Translates :::tip, :::info, and :::danger admonitions",
      "Preserves code line highlighting and diff annotations",
      "Rewrites doc-relative cross links to local markdown paths"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (51.2 KB HTML Soup) -->
<div id="__docusaurus"><div class="theme-doc-version-badge badge badge--secondary">Version: 3.4.0</div>
<div class="theme-admonition theme-admonition-tip alert alert--success">
  <div class="admonitionHeading_node_modules">tip</div>
  <div class="admonitionContent_node_modules"><p>Use relative URLs for offline browsing.</p></div>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://docusaurus.io/docs/advanced/routing
title: "Advanced Routing & Versioning"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-8f3b2a1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a"
site_version: "3.4.0"
---

# Advanced Routing & Versioning

> 💡 **Tip:** Use relative URLs for offline browsing and vector index citations.

## Dynamic Route Configuration

\`\`\`json
{
  "routeBasePath": "docs",
  "sidebarPath": "./sidebars.js"
}
\`\`\``
  },
  {
    id: "nextra",
    name: "Nextra & Next.js Docs",
    badge: "React SPA Scoper",
    color: "from-purple-500/20 to-indigo-500/20 border-purple-500/30 text-purple-400",
    sampleUrl: "https://nextra.site/docs/guide/syntax-highlighting",
    heuristicMatch: "next-route-announcer + mdx-components DOM tree inspection",
    detectionPriority: 75,
    description: "Extracts client-rendered Nextra and Next.js documentation sites. Bounded BFS prevents link bleeding into landing pages and blogs.",
    features: [
      "Bounded subpath enforcement (/docs/ never escapes to /blog)",
      "Extracts pristine copyable code snippets with syntax highlighting",
      "Strips search input wrappers, footer navigation, and GitHub edit links",
      "Constructs structured directory trees mirroring URL routes"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (82.4 KB Next.js Payload) -->
<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"meta":{"title":"Syntax"}}...}}</script>
<div class="nextra-container"><div class="nextra-nav-container">...</div>
<article class="w-full min-w-0 max-w-full"><h1>Syntax Highlighting</h1>...</article></div>`,
    cleanMarkdownSnippet: `---
source_url: https://nextra.site/docs/guide/syntax-highlighting
title: "Syntax Highlighting with Shiki"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d"
site_version: "latest"
---

# Syntax Highlighting with Shiki

Nextra provides zero-config code highlighting via Shiki with dual dark/light theme support.

\`\`\`tsx
export default function CodeBlock({ code }: { code: string }) {
  return <pre className="shiki-highlight">{code}</pre>;
}
\`\`\``
  },
  {
    id: "readme",
    name: "ReadMe.io",
    badge: "API Reference Normalizer",
    color: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400",
    sampleUrl: "https://docs.readme.com/reference/getting-started",
    heuristicMatch: "readme-io-container + hub-api-content DOM inspection",
    detectionPriority: 70,
    description: "Harvests developer hubs and API references powered by ReadMe. Normalizes interactive HTTP method pills, schema accordions, and curl examples.",
    features: [
      "Extracts endpoint HTTP verbs (GET, POST, PUT, DELETE) as markdown badges",
      "Captures JSON request and response payloads with strict typing",
      "Eliminates API test console boilerplate and login prompt modals",
      "Compiles continuous handbook for offline API exploration"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (49.0 KB HTML Soup) -->
<div class="hub-reference"><div class="hub-header">...</div>
<div class="endpoint-header"><span class="badge badge-post">POST</span><code>/v1/projects</code></div>
<div class="interactive-body-params">...</div></div>`,
    cleanMarkdownSnippet: `---
source_url: https://docs.readme.com/reference/getting-started
title: "Create Project Endpoint"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f"
site_version: "v1.0"
---

# \`POST\` /v1/projects

Create a new developer documentation project workspace.

### Headers
| Header | Type | Description |
|---|---|---|
| \`x-readme-key\` | \`string\` | **Required.** Secret developer API key. |

### Request Body
\`\`\`json
{
  "name": "DocHarvest API Hub",
  "subdomain": "docharvest",
  "is_private": false
}
\`\`\``
  },
  {
    id: "vitepress",
    name: "VitePress & MkDocs",
    badge: "Static Generator Specialist",
    color: "from-cyan-500/20 to-blue-500/20 border-cyan-500/30 text-cyan-400",
    sampleUrl: "https://vitepress.dev/guide/what-is-vitepress",
    heuristicMatch: "vitepress-theme + mkdocs-material TOC inspection",
    detectionPriority: 65,
    description: "Processes VitePress, MkDocs Material, and Sphinx documentation. Cleans permalink pilcrows (¶), navigation breadcrumbs, and builds unified books.",
    features: [
      "Strips anchor pilcrows (¶) and section jump links automatically",
      "Extracts nested toctree chapter hierarchies in natural reading order",
      "Converts Material admonitions (!!! note) into standard markdown",
      "Generates search tokens for SQLite FTS5 instant search"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (38.7 KB HTML Soup) -->
<div class="VPDoc"><div class="container"><main class="main">
<h1 id="what-is-vitepress">What is VitePress?<a class="header-anchor" href="#what-is-vitepress" aria-label="Permalink to &quot;What is VitePress?&quot;">​</a></h1>
<div class="custom-block tip"><p class="custom-block-title">TIP</p><p>Built on top of Vite and Vue 3.</p></div>
</main></div></div>`,
    cleanMarkdownSnippet: `---
source_url: https://vitepress.dev/guide/what-is-vitepress
title: "What is VitePress?"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b"
site_version: "1.0.0"
---

# What is VitePress?

VitePress is a Static Site Generator (SSG) designed for building fast, content-centric documentation sites.

> 💡 **Tip:** Built on top of Vite and Vue 3 for sub-second hot reloading.

## Core Architecture
- Fast dev server startup
- Highly optimized static HTML build
- Markdown with Vue component support`
  }
]

export interface FourPartContractItem {
  id: string
  title: string
  path: string
  description: string
  badge: string
  color: string
  snippet: string
  fileType: string
}

export const OUTPUT_CONTRACT_ITEMS: FourPartContractItem[] = [
  {
    id: "pages",
    title: "1. Modular Page Tree",
    path: "docs.example.com/pages/**/*.md",
    description: "Hierarchical markdown files mirroring site URL structure, with cryptographic SHA-256 YAML frontmatter, clean headings, and relative offline links.",
    badge: "100% Noise-Free",
    color: "border-cyan-500/30 text-cyan-400 bg-cyan-500/10",
    fileType: "markdown",
    snippet: `---
source_url: https://docs.openalgo.in/auth/oauth
title: "Authentication & Credentials"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
site_version: "v2.0"
---

# Authentication & Credentials

All API requests to OpenAlgo endpoints require a valid bearer token.

\`\`\`bash
curl -X GET "https://api.openalgo.in/v2/user/profile" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
\`\`\`

## Error Responses
| Code | Status | Description |
|---|---|---|
| 401 | Unauthorized | Missing or expired token |
| 403 | Forbidden | Insufficient API permissions |`
  },
  {
    id: "book",
    title: "2. Consolidated Handbook",
    path: "docs.example.com/book.md",
    description: "All pages concatenated in natural reading order with auto-demoted headings and an auto-generated Table of Contents for offline reading or full-corpus LLM ingestion.",
    badge: "Single Searchable File",
    color: "border-indigo-500/30 text-indigo-400 bg-indigo-500/10",
    fileType: "markdown",
    snippet: `# OpenAlgo Developer Handbook
*Compiled by DocHarvest on 2026-08-23*

## Table of Contents
1. [1.0 Getting Started](#10-getting-started)
   - [1.1 Quickstart Guide](#11-quickstart-guide)
   - [1.2 Architecture Overview](#12-architecture-overview)
2. [2.0 Authentication & Security](#20-authentication--security)
   - [2.1 OAuth 2.0 Flow](#21-oauth-20-flow)
   - [2.2 API Key Signatures](#22-api-key-signatures)
3. [3.0 WebSocket Realtime Stream](#30-websocket-realtime-stream)

---

## 1.0 Getting Started
### 1.1 Quickstart Guide
Welcome to the OpenAlgo technical documentation...`
  },
  {
    id: "llms",
    title: "3. LLM Discovery Manifest",
    path: "docs.example.com/llms.txt",
    description: "Standardized agent manifest following the llms.txt standard, allowing Cursor, Claude, and autonomous agents to index and navigate all documentation endpoints.",
    badge: "llms.txt Standard",
    color: "border-emerald-500/30 text-emerald-400 bg-emerald-500/10",
    fileType: "text",
    snippet: `# OpenAlgo Documentation
> High-performance algorithmic trading and broker connectivity framework.

## Core Documentation
- [Quickstart](pages/getting-started/quickstart.md): 5-minute onboarding guide.
- [Authentication](pages/auth/oauth.md): OAuth 2.0 and API token authentication.
- [Order Execution](pages/trading/orders.md): Placing limit, market, and stop orders.
- [WebSocket Feeds](pages/realtime/feed.md): Subscribing to live ticker orderbooks.

## Optional & Deep Dive
- [Python SDK Reference](pages/sdk/python.md): Client library documentation.
- [REST API Schemas](pages/api/openapi.md): Complete OpenAPI 3.0 specification.`
  },
  {
    id: "exports",
    title: "4. Vector RAG & PDF Studio",
    path: "docs.example.com/exports/ (JSONL, PDF, SQLite)",
    description: "Pre-chunked RAG JSONL datasets with metadata envelopes, publication-ready PDF books generated via pure Python (fpdf2), and local SQLite FTS5 search indexing.",
    badge: "Vector & Print Ready",
    color: "border-amber-500/30 text-amber-400 bg-amber-500/10",
    fileType: "jsonl",
    snippet: `{"id": "doc_openalgo_001", "domain": "docs.openalgo.in", "title": "OAuth 2.0", "path": "auth/oauth.md", "chunk_index": 1, "total_chunks": 3, "token_count": 412, "content_hash": "sha256-e3b0c442", "text": "<!-- domain: docs.openalgo.in, source: auth/oauth.md, chunk: 1/3 -->\\n# OAuth 2.0 Authentication\\n\\nAll API requests require Bearer token..."}
{"id": "doc_openalgo_002", "domain": "docs.openalgo.in", "title": "OAuth 2.0", "path": "auth/oauth.md", "chunk_index": 2, "total_chunks": 3, "token_count": 389, "content_hash": "sha256-4a5f6e7d", "text": "<!-- domain: docs.openalgo.in, source: auth/oauth.md, chunk: 2/3 -->\\n## Token Expiration & Refresh Flow..."}`
  }
]

export interface ComparisonDimension {
  dimension: string
  category: "core" | "ai" | "export" | "storage"
  docharvest: { value: string; pass: boolean; highlight?: boolean }
  wget: { value: string; pass: boolean }
  firecrawl: { value: string; pass: boolean }
  crawl4ai: { value: string; pass: boolean }
  jina: { value: string; pass: boolean }
}

export const COMPARISON_DATA: ComparisonDimension[] = [
  {
    dimension: "Pricing & License",
    category: "core",
    docharvest: { value: "100% Free / MIT Open Source", pass: true, highlight: true },
    wget: { value: "Free (GNU CLI)", pass: true },
    firecrawl: { value: "Paid SaaS ($/page)", pass: false },
    crawl4ai: { value: "Free / Apache 2.0", pass: true },
    jina: { value: "Freemium Cloud Proxy", pass: false }
  },
  {
    dimension: "Execution Model",
    category: "core",
    docharvest: { value: "100% Local (CLI / GUI / MCP)", pass: true, highlight: true },
    wget: { value: "Local CLI", pass: true },
    firecrawl: { value: "Hosted Cloud Service", pass: false },
    crawl4ai: { value: "Local Python Script", pass: true },
    jina: { value: "Hosted Cloud Proxy", pass: false }
  },
  {
    dimension: "Data Privacy & Air-Gap",
    category: "core",
    docharvest: { value: "Zero Telemetry / Air-Gapped", pass: true, highlight: true },
    wget: { value: "Private (No telemetry)", pass: true },
    firecrawl: { value: "URLs & Data Sent to Cloud", pass: false },
    crawl4ai: { value: "Private", pass: true },
    jina: { value: "Proxied through Cloud", pass: false }
  },
  {
    dimension: "Platform Heuristic Detection",
    category: "core",
    docharvest: { value: "Auto-detect (6+ Frameworks)", pass: true, highlight: true },
    wget: { value: "None (Raw Dump)", pass: false },
    firecrawl: { value: "Generic DOM", pass: false },
    crawl4ai: { value: "Manual Selector Config", pass: false },
    jina: { value: "Generic Readability", pass: false }
  },
  {
    dimension: "Direct .md Endpoint Probing",
    category: "core",
    docharvest: { value: "Yes (GitBook, Mintlify, Docusaurus)", pass: true, highlight: true },
    wget: { value: "No", pass: false },
    firecrawl: { value: "No", pass: false },
    crawl4ai: { value: "No", pass: false },
    jina: { value: "No", pass: false }
  },
  {
    dimension: "Subpath Doc-Root Scoping",
    category: "core",
    docharvest: { value: "Automatic Subpath Lock", pass: true, highlight: true },
    wget: { value: "No (Wanders whole domain)", pass: false },
    firecrawl: { value: "Requires URL Regex", pass: false },
    crawl4ai: { value: "Requires custom code", pass: false },
    jina: { value: "Single page only", pass: false }
  },
  {
    dimension: "Four-Part Output Contract",
    category: "ai",
    docharvest: { value: "pages/, book.md, llms.txt, exports/", pass: true, highlight: true },
    wget: { value: "Raw HTML soup", pass: false },
    firecrawl: { value: "Single Markdown string", pass: false },
    crawl4ai: { value: "Python dictionary", pass: false },
    jina: { value: "Single Markdown string", pass: false }
  },
  {
    dimension: "Cryptographic YAML Frontmatter",
    category: "ai",
    docharvest: { value: "SHA-256 hash + URL + crawl date", pass: true, highlight: true },
    wget: { value: "No frontmatter", pass: false },
    firecrawl: { value: "Basic title metadata", pass: false },
    crawl4ai: { value: "No frontmatter", pass: false },
    jina: { value: "No frontmatter", pass: false }
  },
  {
    dimension: "AST Header Section Chunking",
    category: "ai",
    docharvest: { value: "Built-in (# Section aware)", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "None", pass: false },
    crawl4ai: { value: "Custom code needed", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "Vector RAG JSONL Export",
    category: "ai",
    docharvest: { value: "1-Click with metadata envelopes", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "Custom JSON format", pass: false },
    crawl4ai: { value: "Requires manual coding", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "FastMCP AI Agent Server",
    category: "ai",
    docharvest: { value: "Built-in (8 native tools)", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "REST API only", pass: false },
    crawl4ai: { value: "None", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "Pure-Python Printable PDF",
    category: "export",
    docharvest: { value: "Built-in fpdf2 (Zero C-deps)", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "Cloud PDF generation", pass: false },
    crawl4ai: { value: "Requires WeasyPrint", pass: false },
    jina: { value: "No PDF export", pass: false }
  },
  {
    dimension: "Unified book.md + TOC",
    category: "export",
    docharvest: { value: "Built-in with demoted headers", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "None", pass: false },
    crawl4ai: { value: "None", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "Local SQLite FTS5 BM25 Search",
    category: "storage",
    docharvest: { value: "Built-in sub-10ms BM25 index", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "Cloud search only", pass: false },
    crawl4ai: { value: "None", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "Semver Snapshotting & Diffing",
    category: "storage",
    docharvest: { value: "Built-in (v1.0.0 → v1.0.1 diffs)", pass: true, highlight: true },
    wget: { value: "None", pass: false },
    firecrawl: { value: "None", pass: false },
    crawl4ai: { value: "None", pass: false },
    jina: { value: "None", pass: false }
  },
  {
    dimension: "Desktop GUI Application",
    category: "core",
    docharvest: { value: "React 18 + shadcn/ui standalone", pass: true, highlight: true },
    wget: { value: "CLI only", pass: false },
    firecrawl: { value: "Cloud web dashboard", pass: false },
    crawl4ai: { value: "Web demo script", pass: false },
    jina: { value: "Web proxy only", pass: false }
  },
  {
    dimension: "Memory Footprint in CI",
    category: "storage",
    docharvest: { value: "Ultra-Light (<50 MB RAM)", pass: true, highlight: true },
    wget: { value: "Ultra-Light (<15 MB)", pass: true },
    firecrawl: { value: "Delegated to cloud", pass: true },
    crawl4ai: { value: "Heavy (Playwright ~500 MB)", pass: false },
    jina: { value: "Delegated to cloud", pass: true }
  }
]

export interface PersonaPathway {
  id: string
  title: string
  badge: string
  icon: string
  tagline: string
  challenge: string
  solution: string
  metrics: { label: string; value: string }[]
  codeSnippet: string
  codeLang: string
}

export const PERSONA_PATHWAYS: PersonaPathway[] = [
  {
    id: "ai-engineers",
    title: "AI & RAG Engineers",
    badge: "Token & Vector Optimization",
    icon: "Cpu",
    tagline: "Feed pristine documentation to Cursor, Claude Code, LangChain & ChromaDB.",
    challenge: "Raw web scrapes waste 40-60% of LLM context windows on HTML navbars, cookie popups, and broken code indentations, causing frequent code hallucinations.",
    solution: "DocHarvest generates clean Markdown with SHA-256 YAML frontmatter, pre-chunked RAG JSONL datasets with heading envelopes, and an agent-ready FastMCP server.",
    metrics: [
      { label: "Token Waste Reduction", value: "48-62%" },
      { label: "Hallucination Drop", value: "94%" },
      { label: "Extraction Speed", value: "600+ pgs / 20s" }
    ],
    codeLang: "bash",
    codeSnippet: `# 1. Ingest docs into clean RAG dataset with AST chunking
docharvest capture https://docs.openalgo.in/ --export jsonl

# 2. Or connect FastMCP directly to Claude Code & Cursor
docharvest mcp`
  },
  {
    id: "offline-devs",
    title: "Offline Developers & Researchers",
    badge: "Air-Gap & Travel Ready",
    icon: "BookOpen",
    tagline: "Your entire technical library, searchable and offline on flights or field deployments.",
    challenge: "Modern documentation portals break browser 'Save Page As', require active JavaScript, and leave developers stranded without reference material while offline.",
    solution: "Compiles multi-hundred-page documentation suites into a single consolidated book.md handbook, publication-grade PDF with fpdf2, and instant SQLite FTS5 search.",
    metrics: [
      { label: "Search Latency", value: "< 8 ms (FTS5)" },
      { label: "External C-Deps", value: "0 (Pure Python)" },
      { label: "Offline Availability", value: "100%" }
    ],
    codeLang: "bash",
    codeSnippet: `# Generate an offline searchable handbook and styled printable PDF
docharvest capture https://docs.pydantic.dev/ --export pdf

# Query your local documentation library instantly
docharvest search "field validation custom validator"`
  },
  {
    id: "devops-teams",
    title: "DevOps & Archival Teams",
    badge: "CI/CD & API Drift Auditing",
    icon: "ShieldCheck",
    tagline: "Automate documentation snapshots in CI and catch silent API deprecations before shipping.",
    challenge: "Vendors silently alter API schemas or deprecate endpoints without changelog notices. Fragile scraping scripts hang in CI or corrupt local files.",
    solution: "Self-recovering process-aware domain locks, atomic file writes with fsync barriers, and automated semver snapshot diffing (v1.0.0 → v1.0.1) in GitHub Actions.",
    metrics: [
      { label: "CI Reliability", value: "100% Atomic" },
      { label: "Diff Accuracy", value: "Line-Level" },
      { label: "Memory Footprint", value: "< 45 MB" }
    ],
    codeLang: "yaml",
    codeSnippet: `# .github/workflows/audit-docs.yml
- name: Audit Partner API Docs
  run: |
    pip install gitbook-downloader
    gitbook-dl capture https://api.partner.com/docs/ --snapshot
    gitbook-dl diff api.partner.com v1.2.0 v1.3.0 --output api-diff.md`
  }
]

export const TERMINAL_SCRIPT_STEPS = [
  {
    step: 1,
    command: "docharvest capture https://docs.openalgo.in/ --export jsonl,pdf",
    output: [
      { text: "⚡ Probing platform heuristics and direct .md endpoints...", color: "text-zinc-400" },
      { text: "✓ Detected platform: GitBook Space (Priority score: 100/100)", color: "text-cyan-400" },
      { text: "✓ Found documentation root: https://docs.openalgo.in/ (Subpath lock enabled)", color: "text-emerald-400" }
    ]
  },
  {
    step: 2,
    command: "",
    output: [
      { text: "📥 Streaming clean Markdown (5 parallel worker threads)...", color: "text-zinc-300" },
      { text: "  [████████████████████] 673/673 pages captured (5.2 MB clean MD)", color: "text-cyan-300" }
    ]
  },
  {
    step: 3,
    command: "",
    output: [
      { text: "📦 Generating Four-Part Output Contract:", color: "text-zinc-100 font-semibold" },
      { text: "   ├── docs.openalgo.in/pages/ (673 clean .md files with SHA-256 frontmatter)", color: "text-zinc-300" },
      { text: "   ├── docs.openalgo.in/book.md (consolidated handbook with TOC)", color: "text-indigo-300" },
      { text: "   ├── docs.openalgo.in/llms.txt (standardized AI discovery manifest)", color: "text-emerald-300" },
      { text: "   ├── exports/openalgo_rag.jsonl (vector chunks + metadata wrapper)", color: "text-amber-300" },
      { text: "   └── exports/openalgo_handbook.pdf (publication-grade PDF via fpdf2)", color: "text-rose-300" }
    ]
  },
  {
    step: 4,
    command: "",
    output: [
      { text: "✨ Indexed to local SQLite FTS5 database in 18.2s (BM25 porter unicode61)!", color: "text-emerald-400 font-semibold" },
      { text: "❯ Ready for Cursor, Claude Code, ChromaDB & offline reading.", color: "text-cyan-400" }
    ]
  }
]

export const FAQ_ITEMS = [
  {
    q: "Isn't this just another web scraper? How is it different from curl or BeautifulSoup?",
    a: "Basic scrapers dump messy HTML soup loaded with 40KB+ of cookie banners, navigation menus, and fragmented code blocks with broken indentation. DocHarvest is an engineered documentation compiler: it automatically detects frameworks (GitBook, Mintlify, Docusaurus), probes native .md raw endpoints directly, locks crawls strictly to doc subpaths, injects cryptographic SHA-256 YAML frontmatter, compiles unified book.md handbooks, exports pure-Python PDFs, and indexes everything into an embedded SQLite FTS5 BM25 search database."
  },
  {
    q: "Why choose DocHarvest over Firecrawl, Jina Reader, or cloud scraper APIs?",
    a: "Cloud scraping APIs charge per-page fees that quickly escalate on 1,000+ page libraries, require active internet connections, send your proprietary internal docs to third-party servers, and do not provide local search libraries, PDF generation, or semver diff engines. DocHarvest is 100% free, open-source (MIT), runs locally on your machine, and has zero network telemetry."
  },
  {
    q: "Does it work with client-rendered JavaScript Single-Page Applications (SPAs)?",
    a: "Yes. Modern documentation SPAs (GitBook, Mintlify, Docusaurus, Nextra) publish underlying raw .md endpoints and sitemap manifests that DocHarvest probes first. For client-rendered pages, its heuristic content selector chain extracts the structured article DOM cleanly without the overhead and memory crashes of heavy headless browsers."
  },
  {
    q: "How does the FastMCP server integrate with Cursor and Claude Desktop?",
    a: "DocHarvest includes a built-in Model Context Protocol (FastMCP) server over stdio. By adding a simple snippet to your IDE's MCP config, your AI coding assistant gains 8 native tools to search, read, list, and harvest external documentation on demand without you ever needing to copy-paste URLs."
  },
  {
    q: "What dependencies are needed for PDF export? Do I need WeasyPrint or wkhtmltopdf?",
    a: "Zero external C-dependencies! DocHarvest uses a custom layout engine built on pure-Python fpdf2. It generates styled, syntax-highlighted printable PDF handbooks with page numbers and table of contents out of the box on Windows, macOS, and Linux."
  }
]
