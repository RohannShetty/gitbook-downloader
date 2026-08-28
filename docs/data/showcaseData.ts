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
    "https://api.openalgo.in/oauth/token",
    json={"client_id": "pk_live_...", "grant_type": "client_credentials"}
)
\`\`\``
  },
  {
    id: "mintlify",
    name: "Mintlify",
    badge: "MDX Component AST Filter",
    color: "from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400",
    sampleUrl: "https://docs.anthropic.com/en/docs",
    heuristicMatch: "mint.json manifest + <Snippet> & <Card> custom component unnesting",
    detectionPriority: 95,
    description: "Converts Mintlify MDX tags (<Accordion>, <ParamField>, <ResponseField>, <Tab>) into clean standard CommonMark with zero JSX syntax leakage.",
    features: [
      "Translates interactive API playground tabs into multi-language snippets",
      "Expands <ParamField> and <Expandable> into clear tables",
      "Captures navigation hierarchy from mint.json manifests",
      "Strips interactive feedback widgets and analytics scripts"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (38.4 KB JSX/HTML DOM) -->
<div class="mint-article-container" id="content">
  <div class="mint-breadcrumbs">Docs &gt; API &gt; Messages</div>
  <div class="custom-card-group flex gap-4">
    <div class="mint-tab-header active" data-tab="curl">cURL</div>
    <div class="mint-tab-header" data-tab="python">Python</div>
  </div>
  <div class="param-field-root" data-name="model" data-type="string" data-required="true">
    <span class="badge badge-required">Required</span>
    <p>The model that will complete your prompt.</p>
  </div>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://docs.anthropic.com/en/docs/api-reference/messages
title: "Create a Message"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-a1b2c3d4..."
framework: "mintlify"
---

# Create a Message

### Parameters

| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| \`model\` | string | **Yes** | The model that will complete your prompt. |
| \`max_tokens\` | integer | **Yes** | Maximum tokens to generate before stopping. |`
  },
  {
    id: "docusaurus",
    name: "Docusaurus",
    badge: "Versioned Docset Flattener",
    color: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400",
    sampleUrl: "https://reactnative.dev/docs/getting-started",
    heuristicMatch: "docusaurus-plugin-content-docs + __docusaurus state + /docs/next/",
    detectionPriority: 90,
    description: "Detects Docusaurus React SPAs. Traverses version dropdowns, isolates the main <article> container, and strips sticky sidebars and edit-on-GitHub links.",
    features: [
      "Isolates <article> DOM removing sidebar navigation and footer links",
      "Preserves Admonition callouts (:::tip, :::danger, :::note)",
      "Recursively expands React tabs (<Tabs> and <TabItem>)",
      "Extracts frontmatter metadata from Docusaurus injected state"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (49.1 KB Hydration Bundle) -->
<div class="docMainContainer_gTbr">
  <aside class="theme-doc-sidebar-container">...</aside>
  <main class="docMainContainer">
    <div class="theme-admonition theme-admonition-tip">
      <div class="admonitionHeading"><h5>Tip</h5></div>
      <div class="admonitionContent"><p>Use React Native CLI for native code.</p></div>
    </div>
  </main>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://reactnative.dev/docs/getting-started
title: "Environment Setup"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-f5e4d3c2..."
framework: "docusaurus"
---

# Setting up the development environment

> 💡 **Tip:** Use the React Native CLI if you need to build native Swift/Kotlin code.`
  },
  {
    id: "nextra",
    name: "Nextra",
    badge: "Next.js Static Content Extractor",
    color: "from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400",
    sampleUrl: "https://swr.vercel.app/docs/getting-started",
    heuristicMatch: "nextra-content + next-data-payload + _meta.json",
    detectionPriority: 85,
    description: "Extracts docs built with Vercel Nextra. Parses _meta.json files to build exact navigation hierarchy and extracts clean article content.",
    features: [
      "Parses _meta.json for exact menu hierarchy and ordering",
      "Strips Next.js page transitions and script hydration tags",
      "Extracts clean code blocks with syntax highlighting indicators",
      "Preserves Nextra Callout and Steps components"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (31.7 KB HTML) -->
<article class="nextra-body nextra-content">
  <div class="nextra-breadcrumb">...</div>
  <h1 class="nextra-heading">Getting Started</h1>
  <div class="nextra-callout nextra-callout-info">
    <div class="nextra-callout-icon">...</div>
    <div class="nextra-callout-text">SWR is a React Hooks library for data fetching.</div>
  </div>
</article>`,
    cleanMarkdownSnippet: `---
source_url: https://swr.vercel.app/docs/getting-started
title: "Getting Started"
crawl_date: "2026-08-23T16:42:19Z"
content_hash: "sha256-b7a6c5d4..."
framework: "nextra"
---

# Getting Started

> ℹ️ **Note:** SWR is a React Hooks library for data fetching.

\`\`\`bash
npm install swr
\`\`\``
  },
  {
    id: "readme",
    name: "ReadMe.io",
    badge: "OAS 3.0 API Schema Unfolder",
    color: "from-sky-500/20 to-blue-500/20 border-sky-500/30 text-sky-400",
    sampleUrl: "https://docs.readme.com/reference",
    heuristicMatch: "readme.io/reference/ + /api-explorer/ + swagger schema parser",
    detectionPriority: 80,
    description: "Unfolds ReadMe interactive API docs. Extracts OpenAPI endpoints, query parameter schemas, and response examples into clear markdown tables.",
    features: [
      "Converts OpenAPI JSON specifications into structured markdown",
      "Extracts request headers, authentication requirements, and payload bodies",
      "Strips interactive 'Try It' test consoles and API key inputs",
      "Consolidates response status codes (200, 400, 401, 500) with JSON mocks"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (44.5 KB API Explorer DOM) -->
<div class="api-explorer-root" data-method="POST" data-endpoint="/v1/users">
  <div class="interactive-form-console"><input name="api_key" type="password" />...</div>
  <div class="param-row"><code>email</code><span>string (required)</span></div>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://api.example.com/reference/create-user
title: "Create User"
http_method: "POST"
endpoint: "/v1/users"
---

# Create User \`POST /v1/users\`

### Body Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| \`email\` | string | **Yes** | User email address. |`
  },
  {
    id: "vitepress",
    name: "VitePress",
    badge: "Vue-Powered Static Tree Compiler",
    color: "from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-400",
    sampleUrl: "https://vitepress.dev/guide/what-is-vitepress",
    heuristicMatch: "vp-doc + vitepress-nav + .vitepress/config.ts",
    detectionPriority: 75,
    description: "Harvests VitePress documentation portals. Extracts frontmatter, table of contents, and multi-language code snippets without Vue template tags.",
    features: [
      "Isolates .vp-doc markdown container",
      "Transforms Vue custom containers (::: info, ::: warning)",
      "Preserves code group tabs with file name badges",
      "Generates unified offline handbook from sidebar configuration"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (29.2 KB Vue DOM) -->
<div class="VPContent">
  <div class="VPDoc">
    <div class="custom-block tip"><p class="custom-block-title">TIP</p><p>VitePress is built on Vite.</p></div>
  </div>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://vitepress.dev/guide/what-is-vitepress
title: "What is VitePress?"
crawl_date: "2026-08-23T16:42:19Z"
---

# What is VitePress?

> 💡 **Tip:** VitePress is built on Vite and Vue 3.`
  },
  {
    id: "mkdocs",
    name: "MkDocs",
    badge: "Material Python Documentation Harvester",
    color: "from-indigo-500/20 to-violet-500/20 border-indigo-500/30 text-indigo-400",
    sampleUrl: "https://squidfunk.github.io/mkdocs-material/",
    heuristicMatch: "md-content + mkdocs.yml + search_index.json",
    detectionPriority: 70,
    description: "Parses MkDocs and Material for MkDocs. Extracts complete documentation hierarchy, search_index.json files, and code tabs.",
    features: [
      "Direct extraction of pre-compiled search_index.json for instant indexing",
      "Strips Material for MkDocs search modal and header navigation",
      "Preserves pymdownx code blocks and content tabs",
      "Extracts mathematical formulas (MathJax / KaTeX) cleanly"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (35.1 KB MkDocs HTML) -->
<div class="md-content">
  <article class="md-content__inner md-typeset">
    <h1>Material for MkDocs</h1>
    <div class="admonition note"><p class="admonition-title">Note</p><p>Built with Python.</p></div>
  </article>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://squidfunk.github.io/mkdocs-material/
title: "Material for MkDocs"
crawl_date: "2026-08-23T16:42:19Z"
---

# Material for MkDocs

> ℹ️ **Note:** Built with Python and modern CSS.`
  },
  {
    id: "readthedocs",
    name: "ReadTheDocs",
    badge: "Sphinx / reStructuredText AST",
    color: "from-teal-500/20 to-cyan-500/20 border-teal-500/30 text-teal-400",
    sampleUrl: "https://docs.readthedocs.io/en/stable/",
    heuristicMatch: "readthedocs-data + div.rst-content + div.document",
    detectionPriority: 60,
    description: "Converts Sphinx and ReadTheDocs portals. Handles multi-version flyouts, strips Sphinx search bars, and converts reStructuredText directive blocks to clean CommonMark.",
    features: [
      "Translates Sphinx directives (.. note::, .. code-block::) into Markdown blocks",
      "Strips RTD flyout menus, search modals, and build version banners",
      "Extracts full API signatures, method docstrings, and parameter tables",
      "Preserves cross-page intersphinx reference links"
    ],
    rawHtmlSnippet: `<!-- Raw Scraper Output (41.3 KB Sphinx HTML) -->
<div class="rst-content">
  <div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">
    <h1>Read the Docs Documentation</h1>
    <div class="admonition tip"><p class="admonition-title">Tip</p><p>Sphinx documentation builder.</p></div>
  </div>
</div>`,
    cleanMarkdownSnippet: `---
source_url: https://docs.readthedocs.io/en/stable/
title: "Read the Docs Documentation"
crawl_date: "2026-08-28T16:42:19Z"
framework: "readthedocs"
---

# Read the Docs Documentation

> 💡 **Tip:** Built with Sphinx documentation builder.`
  }
]

export const CONTRACT_FORMATS = [
  {
    id: "markdown",
    title: "1. Consolidated Markdown",
    subtitle: "Unified book.md for LLM System Prompts",
    badge: "Universal Context",
    fileExt: "book.md",
    description: "Merges the entire documentation portal into a single coherent, top-to-bottom Markdown file with an automatic table of contents and internal anchor links.",
    features: [
      "Automated hierarchical Table of Contents",
      "Relative link remapping to internal document anchors",
      "Zero redundant headers, sidebars, or footers",
      "Perfect for pasting directly into Claude Project Knowledge or ChatGPT Custom GPTs"
    ]
  },
  {
    id: "rag",
    title: "2. Vector RAG JSONL",
    subtitle: "Chunked & Tokenized for Vector Databases",
    badge: "RAG & Vector Search",
    fileExt: "dataset.jsonl",
    description: "Every page is parsed into semantic chunks with token counts, SHA-256 content hashes, breadcrumb taxonomies, and source URL metadata.",
    features: [
      "Pre-calculated token counts (cl100k_base / o200k_base compatible)",
      "Cryptographic SHA-256 content hashes for incremental synchronization",
      "Breadcrumb taxonomy arrays: ['API Reference', 'Orders', 'Create']",
      "Direct drop-in for LangChain, LlamaIndex, ChromaDB, and Pinecone"
    ]
  },
  {
    id: "llmstxt",
    title: "3. Standard llms.txt",
    subtitle: "The AI Discovery Manifest Standard",
    badge: "AI Discovery Manifest",
    fileExt: "llms.txt",
    description: "Implements the official llms.txt standard proposed for AI agent consumption, organizing core guides, API schemas, and secondary links.",
    features: [
      "Structured # Heading with brief summary",
      "## Docs Section with clean markdown links",
      "## Optional Section for advanced reference",
      "Standard compliance for automated Cursor & Claude indexing"
    ]
  },
  {
    id: "pdf",
    title: "4. Publication-Grade PDF",
    subtitle: "Formatted Offline Printable Handbook",
    badge: "Offline Printable",
    fileExt: "handbook.pdf",
    description: "Built on pure-Python fpdf2 layout engine with zero C-dependencies. Generates a beautifully styled, searchable offline PDF with cover page, TOC, and syntax-highlighted code.",
    features: [
      "Pure-Python fpdf2 rendering (zero WeasyPrint/wkhtmltopdf dependencies)",
      "Automatic multi-level Table of Contents with page number targets",
      "Syntax-highlighted code blocks with rounded container styling",
      "Page headers, footers, and timestamp watermarks"
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
    a: "Yes. Modern documentation SPAs (GitBook, Mintlify, Docusaurus, Nextra, VitePress) publish underlying raw .md endpoints and sitemaps that DocHarvest probes first. For purely client-rendered SPAs (like omp.sh), DocHarvest includes an opt-in Playwright headless rendering engine (--render) to execute client-side JavaScript before compilation."
  },
  {
    q: "How does the FastMCP server integrate with Cursor and Claude Desktop?",
    a: "DocHarvest includes a built-in Model Context Protocol (FastMCP v2) server over stdio. By adding a simple snippet to your IDE's MCP config, your AI coding assistant gains 10 native tools, MCP Resources, and MCP Prompts to search, read, list, graph-navigate, and harvest external documentation on demand without you ever needing to copy-paste URLs."
  },
  {
    q: "What dependencies are needed for PDF export? Do I need WeasyPrint or wkhtmltopdf?",
    a: "Zero external C-dependencies! DocHarvest uses a custom layout engine built on pure-Python fpdf2. It generates styled, syntax-highlighted printable PDF handbooks with page numbers and table of contents out of the box on Windows, macOS, and Linux."
  }
]
