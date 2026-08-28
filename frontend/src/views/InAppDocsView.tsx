import React, { useState } from "react"
import {
  BookOpen,
  Sparkles,
  Terminal,
  Cpu,
  Layers,
  Search,
  Download,
  Copy,
  Check,
  Code,
  ShieldCheck,
  Globe,
  FileText,
  Boxes,
  HelpCircle,
  ExternalLink
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

interface DocSection {
  id: string
  title: string
  category: string
  icon: React.ElementType
  content: React.ReactNode
}

export const InAppDocsView: React.FC = () => {
  const [activeSectionId, setActiveSectionId] = useState<string>("overview")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  const handleCopyCode = (key: string, code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedKey(key)
    toast.success("Snippet copied to clipboard!")
    setTimeout(() => setCopiedKey(null), 2000)
  }

  const sections: DocSection[] = [
    {
      id: "overview",
      title: "Overview & Architecture",
      category: "Getting Started",
      icon: Sparkles,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              What is DocHarvest?
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              DocHarvest (package: <code className="font-mono text-cyan-400">gitbook-downloader</code>) is a high-performance, local-first documentation compiler and AI context platform. It transforms full documentation portals into pristine, LLM-optimized Markdown, vector RAG datasets, and styled offline PDF handbooks.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs font-semibold">
                <Globe className="h-4 w-4" /> Zero-Noise Extraction
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Directly probes raw <code className="font-mono text-foreground">.md</code> endpoints and performs AST-based DOM stripping to eliminate up to 89% of navigation boilerplate and cookie banners.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold">
                <Boxes className="h-4 w-4" /> 4-Part Output Contract
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Every crawl produces modular <code className="font-mono text-foreground">pages/</code>, a consolidated <code className="font-mono text-foreground">book.md</code>, a standardized <code className="font-mono text-foreground">llms.txt</code>, and cryptographic metadata manifests.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <div className="flex items-center gap-2 text-purple-400 font-mono text-xs font-semibold">
                <Cpu className="h-4 w-4" /> Native FastMCP Server
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Exposes 8 native Model Context Protocol tools and resources to Cursor, Claude Code, Windsurf, Zed, and 10+ AI IDEs over stdio.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold font-mono text-foreground">
              Standard Output Tree Structure
            </h3>
            <div className="relative rounded-xl border border-border bg-[#090d16] p-4 text-xs font-mono text-slate-300">
              <pre className="overflow-x-auto leading-relaxed">{`data/
└── docs.openalgo.in/
    ├── pages/                     # Modular individual markdown files
    │   ├── 001_quickstart.md
    │   └── 002_api_reference.md
    ├── book.md                    # Consolidated handbook with hierarchical TOC
    ├── llms.txt                   # Standardized AI discovery manifest
    ├── exports/
    │   ├── openalgo_rag.jsonl     # Tokenized vector chunks + metadata
    │   └── openalgo_handbook.pdf  # Pure-Python styled PDF handbook
    └── .manifest.json             # Cryptographic hashes, crawl metrics & engine version`}</pre>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "providers",
      title: "8 Documentation Providers",
      category: "Core Engine",
      icon: Layers,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              Supported Documentation Platforms
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              DocHarvest features dedicated, priority-ordered parsers that isolate clean article content and strip headers, footers, sidebars, anchor hashes, and cookie banners:
            </p>
          </div>

          <div className="overflow-hidden rounded-xl border border-border bg-card/40">
            <table className="w-full text-left text-xs font-sans">
              <thead className="border-b border-border bg-muted/50 font-mono text-[11px] text-muted-foreground">
                <tr>
                  <th className="p-3">Platform</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Discovery Method</th>
                  <th className="p-3">Content Target</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-muted-foreground">
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">GitBook</td>
                  <td className="p-3 font-mono text-cyan-400">100</td>
                  <td className="p-3">.md endpoint probing & space discovery</td>
                  <td className="p-3 font-mono text-[11px]">.page-inner, article</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">Mintlify</td>
                  <td className="p-3 font-mono text-cyan-400">90</td>
                  <td className="p-3">mintlify.json & CDN asset anchors</td>
                  <td className="p-3 font-mono text-[11px]">#content, article</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">Docusaurus</td>
                  <td className="p-3 font-mono text-cyan-400">80</td>
                  <td className="p-3">sitemap.xml & docusaurus.config</td>
                  <td className="p-3 font-mono text-[11px]">article, .markdown</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">Nextra</td>
                  <td className="p-3 font-mono text-cyan-400">75</td>
                  <td className="p-3">Next.js routes & nextra scripts</td>
                  <td className="p-3 font-mono text-[11px]">main.nextra-content</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">VitePress</td>
                  <td className="p-3 font-mono text-cyan-400">72</td>
                  <td className="p-3">VitePress theme anchors & route index</td>
                  <td className="p-3 font-mono text-[11px]">div.vp-doc, div.VPContent</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">MkDocs</td>
                  <td className="p-3 font-mono text-cyan-400">70</td>
                  <td className="p-3">search_index.json & Material theme</td>
                  <td className="p-3 font-mono text-[11px]">article.md-content__inner</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">ReadMe.io</td>
                  <td className="p-3 font-mono text-cyan-400">65</td>
                  <td className="p-3">sitemap.xml, llms.txt & hub routes</td>
                  <td className="p-3 font-mono text-[11px]">div.rm-Article, div.rm-Markdown</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">ReadTheDocs</td>
                  <td className="p-3 font-mono text-cyan-400">60</td>
                  <td className="p-3">Sphinx sitemap & sphinxsidebar</td>
                  <td className="p-3 font-mono text-[11px]">div.document[role="main"]</td>
                </tr>
                <tr className="hover:bg-muted/20">
                  <td className="p-3 font-semibold text-foreground">Generic HTML</td>
                  <td className="p-3 font-mono text-slate-400">0</td>
                  <td className="p-3">BFS link crawler + sitemap</td>
                  <td className="p-3 font-mono text-[11px]">main, article, [role="main"]</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )
    },
    {
      id: "spa-render",
      title: "Headless Browser Rendering (SPAs)",
      category: "Core Engine",
      icon: Globe,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              Dynamic JavaScript SPAs & Anti-Bot Handling
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              Certain documentation portals (such as client-rendered React/Vue SPAs like <code className="font-mono text-cyan-400">omp.sh/docs</code>) return an empty skeletal shell when fetched over plain HTTP. DocHarvest provides loud diagnostics and an optional Playwright headless renderer.
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold font-mono text-foreground">
              1. Installing the Headless Renderer Extra
            </h3>
            <div className="relative rounded-xl border border-border bg-[#090d16] p-4 text-xs font-mono text-slate-300">
              <button
                onClick={() => handleCopyCode("render_install", 'pip install "gitbook-downloader[render]"\nplaywright install chromium')}
                className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
              >
                {copiedKey === "render_install" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              </button>
              <pre>{`pip install "gitbook-downloader[render]"
playwright install chromium`}</pre>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold font-mono text-foreground">
              2. Executing a Headless SPA Crawl
            </h3>
            <div className="relative rounded-xl border border-border bg-[#090d16] p-4 text-xs font-mono text-slate-300">
              <button
                onClick={() => handleCopyCode("render_cli", "docharvest crawl https://omp.sh/docs --render")}
                className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
              >
                {copiedKey === "render_cli" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              </button>
              <pre>{`# CLI Crawl with Headless JavaScript Execution
docharvest crawl https://omp.sh/docs --render`}</pre>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "cli",
      title: "CLI Command Reference",
      category: "Usage & CLI",
      icon: Terminal,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              Command Line Interface Reference
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              DocHarvest provides a comprehensive CLI accessible via <code className="font-mono text-cyan-400">docharvest</code> or <code className="font-mono text-cyan-400">gitbook-dl</code>:
            </p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <span className="font-mono text-xs font-semibold text-foreground">1. Basic Crawl & Extraction</span>
              <div className="relative rounded-xl border border-border bg-[#090d16] p-3 text-xs font-mono text-slate-300">
                <button
                  onClick={() => handleCopyCode("cli_crawl", "docharvest crawl https://docs.openalgo.in/ --rag --pdf")}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
                >
                  {copiedKey === "cli_crawl" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                </button>
                <pre>{`docharvest crawl https://docs.openalgo.in/ --rag --pdf`}</pre>
              </div>
            </div>

            <div className="space-y-2">
              <span className="font-mono text-xs font-semibold text-foreground">2. Path Scoping & Worker Limits</span>
              <div className="relative rounded-xl border border-border bg-[#090d16] p-3 text-xs font-mono text-slate-300">
                <button
                  onClick={() => handleCopyCode("cli_scope", "docharvest crawl https://docs.example.com/ --scope /api/ --workers 12 --max-pages 50")}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
                >
                  {copiedKey === "cli_scope" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                </button>
                <pre>{`docharvest crawl https://docs.example.com/ --scope /api/ --workers 12 --max-pages 50`}</pre>
              </div>
            </div>

            <div className="space-y-2">
              <span className="font-mono text-xs font-semibold text-foreground">3. Full-Text Search</span>
              <div className="relative rounded-xl border border-border bg-[#090d16] p-3 text-xs font-mono text-slate-300">
                <button
                  onClick={() => handleCopyCode("cli_search", 'docharvest search "OAuth 2.0 authentication"')}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
                >
                  {copiedKey === "cli_search" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                </button>
                <pre>{`docharvest search "OAuth 2.0 authentication"`}</pre>
              </div>
            </div>

            <div className="space-y-2">
              <span className="font-mono text-xs font-semibold text-foreground">4. Launch MCP Server or GUI</span>
              <div className="relative rounded-xl border border-border bg-[#090d16] p-3 text-xs font-mono text-slate-300">
                <button
                  onClick={() => handleCopyCode("cli_mcp", "docharvest mcp\n# or\ndocharvest --gui")}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
                >
                  {copiedKey === "cli_mcp" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                </button>
                <pre>{`docharvest mcp
# or launch GUI:
docharvest --gui`}</pre>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "mcp",
      title: "AI Agent Integration (FastMCP v2)",
      category: "AI & Agents",
      icon: Cpu,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              Model Context Protocol (MCP v2) Integration
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              DocHarvest exposes 8 native tools, MCP Resources, and MCP Prompts over standard input/output (<code className="font-mono text-cyan-400">stdio</code>). Compatible with Cursor, Claude Desktop, Claude Code, Windsurf, Zed, and 10+ other harnesses.
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold font-mono text-foreground">
              All 8 Native MCP Tools
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">download_docs(url, ...)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">Crawl & extract any documentation site into Markdown & llms.txt.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">search_docs(query, domain, limit)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">BM25 SQLite FTS5 search across local indexed documentation.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">get_doc(domain, version)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">Read full compiled documentation handbook or preview.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">list_domains()</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">List all harvested documentation portals in local library.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">diff_versions(domain, v1, v2)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">Compute unified diffs and line stats between two snapshots.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">list_versions(domain)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">List available captured snapshots for a domain.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">export_docs(domain, format)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">Export docset to Markdown, JSONL, or RAG formats.</p>
              </div>
              <div className="p-3 rounded-lg border border-border bg-card/60">
                <span className="text-cyan-400 font-semibold">get_changelog(domain)</span>
                <p className="text-[11px] font-sans text-muted-foreground mt-1">Auto-generate version changelogs across captured iterations.</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold font-mono text-foreground">
              Example Claude Desktop Config (<code className="text-cyan-400">claude_desktop_config.json</code>)
            </h3>
            <div className="relative rounded-xl border border-border bg-[#090d16] p-4 text-xs font-mono text-slate-300">
              <button
                onClick={() => handleCopyCode("mcp_claude", JSON.stringify({
                  mcpServers: {
                    docharvest: {
                      command: "docharvest",
                      args: ["mcp"]
                    }
                  }
                }, null, 2))}
                className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
              >
                {copiedKey === "mcp_claude" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              </button>
              <pre>{`{
  "mcpServers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}`}</pre>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "exports",
      title: "RAG & PDF Export Studio",
      category: "Exports",
      icon: FileText,
      content: (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold font-mono tracking-tight text-foreground">
              Downstream Vector Ingestion & Printable Books
            </h2>
            <p className="text-xs leading-relaxed text-muted-foreground">
              DocHarvest bridges the gap between raw documentation websites and downstream AI systems:
            </p>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <h3 className="text-sm font-semibold font-mono text-cyan-400">
                1. Vector RAG JSONL Chunks
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                AST header-split markdown chunks with token metadata, URLs, page titles, and content hashes ready for LangChain, LlamaIndex, ChromaDB, and Pinecone vector stores.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <h3 className="text-sm font-semibold font-mono text-emerald-400">
                2. Pure-Python PDF Handbooks (fpdf2)
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                High-contrast printable PDF books with automatic cover page, table of contents, syntax highlighting, and page numbers generated with pure Python (zero heavy headless browser dependencies).
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/80 bg-card/60 space-y-2">
              <h3 className="text-sm font-semibold font-mono text-purple-400">
                3. Standardized llms.txt Manifest
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Automatically created at the root of every harvested documentation folder to adhere to standardized LLM agent context discovery protocols.
              </p>
            </div>
          </div>
        </div>
      )
    }
  ]

  const filteredSections = sections.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const activeSection = sections.find((s) => s.id === activeSectionId) || sections[0]

  return (
    <div className="flex h-full flex-col bg-background text-foreground select-none">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border bg-card/80 px-6 py-4 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
            <BookOpen className="h-4 w-4" />
          </div>
          <div>
            <h1 className="text-base font-bold font-mono tracking-tight text-foreground">
              In-App Documentation & Guides
            </h1>
            <p className="text-xs text-muted-foreground">
              Comprehensive reference for DocHarvest v11 features, CLI commands, and MCP v2 tools.
            </p>
          </div>
        </div>

        {/* Search */}
        <div className="relative w-64">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search documentation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 text-xs bg-background/50 border-border/60"
          />
        </div>
      </div>

      {/* Main Split Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <aside className="w-64 border-r border-border bg-card/40 backdrop-blur-sm p-4 overflow-y-auto space-y-4">
          <div className="space-y-1">
            {filteredSections.map((sec) => {
              const Icon = sec.icon
              const isActive = activeSectionId === sec.id
              return (
                <button
                  key={sec.id}
                  onClick={() => setActiveSectionId(sec.id)}
                  className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs transition-colors ${
                    isActive
                      ? "bg-primary/15 text-primary font-semibold border border-primary/25 shadow-xs"
                      : "text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                  }`}
                >
                  <Icon className={`h-3.5 w-3.5 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                  <span className="truncate">{sec.title}</span>
                </button>
              )
            })}
          </div>
        </aside>

        {/* Active Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 font-sans">
          <div className="max-w-4xl mx-auto space-y-6">
            {activeSection.content}
          </div>
        </main>
      </div>
    </div>
  )
}
