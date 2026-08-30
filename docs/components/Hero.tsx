'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Download, ArrowRight, Play, Check, Copy, Sparkles, Layers, Cpu, FileText } from 'lucide-react';
import { WindowsIcon, PythonIcon } from './Icons';
import { VERSION, DOWNLOAD_URLS } from '../lib/version';

interface HeroProps {
  onOpenInstallModal: () => void;
}

const TERMINAL_LOGS = [
  { text: "$ docharvest crawl https://docs.openalgo.in/v/v2.0 --rag --pdf --fast-ast", color: "text-cyan/40 font-bold" },
  { text: "⚡ [Heuristic] Detected GitBook Space engine (version selector: v2.0)", color: "text-cyan/30" },
  { text: "🔍 Discovering documentation tree via sitemap and AST BFS...", color: "text-cyan/40" },
  { text: "   ├── Discovered: /api-reference/oauth [3.2 KB raw .md]", color: "text-cyan/30" },
  { text: "   ├── Discovered: /api-reference/orders [14.8 KB raw .md]", color: "text-cyan/30" },
  { text: "   ├── Discovered: /api-reference/positions [6.1 KB raw .md]", color: "text-cyan/30" },
  { text: "   └── Discovered: /algorithms/quickstart [8.4 KB raw .md]", color: "text-cyan/30" },
  { text: "📥 Parallel AST crawl: 364 pages harvested in 18.2s (20.0 pages/sec)", color: "text-cyan/40 font-semibold" },
  { text: "📦 Compiling outputs:", color: "text-cyan/30 font-medium" },
  { text: "   ├── book.md (consolidated single handbook with TOC)", color: "text-cyan/30" },
  { text: "   ├── llms.txt (standardized AI context manifest)", color: "text-cyan/30" },
  { text: "   ├── openalgo_rag.jsonl (vector chunks + SHA-256 metadata)", color: "text-cyan/30" },
  { text: "   └── openalgo_handbook.pdf (publication-grade printable PDF)", color: "text-cyan/30" },
  { text: "✨ FastMCP server listening on stdio. Ready for Cursor & Claude Code!", color: "text-cyan/30 font-bold" }
];

const HERO_AGENTS = [
  { id: 'cursor', name: 'Cursor' },
  { id: 'claude', name: 'Claude Code' },
  { id: 'opencode', name: 'OpenCode' },
  { id: 'pi', name: 'Pi / Omp.sh' },
  { id: 'windsurf', name: 'Windsurf' },
  { id: 'codex', name: 'Codex CLI' }
];

export function Hero({ onOpenInstallModal }: HeroProps) {
  const [selectedAgentId, setSelectedAgentId] = useState('cursor');
  const [copiedPip, setCopiedPip] = useState(false);
  const [activeTab, setActiveTab] = useState<'terminal' | 'ast' | 'vector' | 'mcp-stdio'>('terminal');

  const copyPipCommand = () => {
    navigator.clipboard.writeText('pip install gitbook-downloader');
    setCopiedPip(true);
    setTimeout(() => setCopiedPip(false), 2000);
  };

  return (
    <section className="relative overflow-hidden border-b border-border bg-background py-16 lg:py-24">
      {/* Background Grid & Radial Glows */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-[size:3.5rem_3.5rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />
      <div className="absolute top-0 left-1/4 h-[400px] w-[400px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 h-[300px] w-[300px] bg-card/50 rounded-full blur-[100px] pointer-events-none" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Headline & Action CTAs */}
          <div className="lg:col-span-6 flex flex-col items-start space-y-6">
            
            {/* Version & Capability Badge */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border/50 bg-card/50 text-xs font-mono font-bold text-cyan"
            >
              <Sparkles className="h-3.5 w-3.5 text-cyan" />
              <span>DocHarvest v{VERSION} — Local-First AI AST Compiler</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.08] text-foreground"
            >
              Turn any documentation into <span className="text-primary font-bold">pure context</span> for Cursor, Claude Code &amp; OpenCode.
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base sm:text-lg text-muted-foreground font-mono leading-relaxed"
            >
              Crawl GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe &amp; JS SPAs with AST precision. Strip 89% of HTML noise and connect directly via <code className="text-cyan font-bold">FastMCP v2</code> or offline PDFs.
            </motion.p>

            {/* Quick Agent Selector Pills */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.25 }}
              className="w-full space-y-2 pt-1"
            >
              <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block">
                1-Click Connect to Your Favorite Coding Harness:
              </span>
              <div className="flex flex-wrap items-center gap-1.5">
                {HERO_AGENTS.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgentId(agent.id)}
                    aria-pressed={selectedAgentId === agent.id}
                    className={`px-2.5 py-1 rounded-md border font-mono text-[0.70rem] font-semibold transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                      selectedAgentId === agent.id
                        ? 'border-border/50 bg-card/50 text-cyan font-bold shadow-xs'
                        : 'border-border/80 bg-card text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {agent.name}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Primary Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-wrap items-center gap-3 pt-1 w-full"
            >
              <a
                href={DOWNLOAD_URLS.windows}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-primary px-5 text-xs font-mono font-bold text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/25 transition-all duration-200"
              >
                <WindowsIcon className="h-4 w-4" />
                <span>Download for Windows (.exe)</span>
              </a>

              <button
                onClick={onOpenInstallModal}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-border bg-card px-5 text-xs font-mono font-bold text-foreground hover:border-primary/50 hover:bg-secondary transition-all duration-200 cursor-pointer focus-visible:outline-2 focus-visible:outline-primary"
              >
                <PythonIcon className="h-4 w-4" />
                <span>Install via PyPI / uvx</span>
              </button>
            </motion.div>

            {/* Install Pip Copy Bar */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="flex items-center gap-2 px-3.5 py-2 rounded-md border border-border/80 bg-card/80 font-mono text-xs text-muted-foreground w-full"
            >
              <span className="text-cyan">&gt;</span>
              <code className="flex-1 text-foreground font-semibold">pip install gitbook-downloader</code>
              <button
                onClick={copyPipCommand}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-secondary hover:bg-primary/20 hover:text-primary transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary text-[11px]"
                aria-label="Copy pip install command"
              >
                {copiedPip ? <Check className="h-3.5 w-3.5 text-cyan/50" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedPip ? 'Copied' : 'Copy'}</span>
              </button>
            </motion.div>

            {/* Proof Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2 w-full font-mono text-xs border-t border-border/80">
              <div className="space-y-0.5">
                <span className="text-muted-foreground text-[10px] block">THROUGHPUT</span>
                <span className="font-bold text-cyan">20 pgs/sec</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-muted-foreground text-[10px] block">TOKEN SAVINGS</span>
                <span className="font-bold text-emerald">89% Reduction</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-muted-foreground text-[10px] block">PRIVACY</span>
                <span className="font-bold text-foreground">100% Local</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-muted-foreground text-[10px] block">AGENT MODELS</span>
                <span className="font-bold text-cyan">15+ Harnesses</span>
              </div>
            </div>

          </div>

          {/* Right Column: Simulated Live Scraping Terminal */}
          <div className="lg:col-span-6 relative">
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="border border-border rounded-xl bg-[#0d0d12] shadow-2xl overflow-hidden"
            >
              {/* Terminal Window Title Bar */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-border/80 bg-card/95">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-card/50" />
                  <div className="w-3 h-3 rounded-full bg-card/50" />
                  <div className="w-3 h-3 rounded-full bg-card/50" />
                  <span className="ml-2 font-mono text-[11px] text-muted-foreground">
                    docharvest@terminal — v{VERSION}
                  </span>
                </div>
                
                {/* Mode Selector */}
                <div className="flex items-center gap-1 font-mono text-[10px]">
                  <button
                    onClick={() => setActiveTab('terminal')}
                    role="tab"
                    aria-selected={activeTab === 'terminal'}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                      activeTab === 'terminal' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Crawl Logs
                  </button>
                  <button
                    onClick={() => setActiveTab('ast')}
                    role="tab"
                    aria-selected={activeTab === 'ast'}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                      activeTab === 'ast' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    AST Filter
                  </button>
                  <button
                    onClick={() => setActiveTab('vector')}
                    role="tab"
                    aria-selected={activeTab === 'vector'}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                      activeTab === 'vector' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Vector JSONL
                  </button>
                  <button
                    onClick={() => setActiveTab('mcp-stdio')}
                    role="tab"
                    aria-selected={activeTab === 'mcp-stdio'}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                      activeTab === 'mcp-stdio' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    MCP stdio
                  </button>
                </div>
              </div>

              {/* Terminal Body Content */}
              <div className="p-4 sm:p-5 font-mono text-xs leading-relaxed space-y-2 h-[340px] overflow-y-auto bg-[#0A0A0E]">
                {activeTab === 'terminal' && (
                  <div className="space-y-1.5 animate-fadeIn">
                    {TERMINAL_LOGS.map((log, index) => (
                      <div key={index} className={log.color}>
                        {log.text}
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'ast' && (
                  <div className="space-y-2 text-cyan/30 animate-fadeIn">
                    <div className="text-cyan/40 font-bold">// AST Heuristic Boundary Isolation:</div>
                    <pre className="text-[11px] text-cyan/40 bg-black/40 p-3 rounded border border-border/60 overflow-x-auto">
{`def extract_clean_article(soup: BeautifulSoup) -> str:
    # 1. Eliminate navigation, footers, & cookie banners
    for noise in soup.select("nav, footer, .sidebar, .cookie-banner"):
        noise.decompose()
        
    # 2. Extract structured Markdown preserving code blocks
    article = soup.find("article") or soup.find("main")
    return markdownify(str(article), heading_style="ATX")`}
                    </pre>
                    <div className="text-cyan/40 text-[11px]">
                      ✓ Extracted 364 articles with zero wrapper bloat (89% token reduction).
                    </div>
                  </div>
                )}

                {activeTab === 'vector' && (
                  <div className="space-y-2 text-cyan/30 animate-fadeIn">
                    <div className="text-cyan/40 font-bold">// RAG JSONL Vector Payload Chunk:</div>
                    <pre className="text-[11px] text-cyan/40 bg-black/40 p-3 rounded border border-border/60 overflow-x-auto">
{`{
  "id": "openalgo_oauth_v2",
  "source_url": "https://docs.openalgo.in/v/v2.0/auth",
  "title": "OAuth 2.0 Authentication",
  "content_hash": "sha256-e3b0c44...",
  "tokens": 412,
  "chunk_text": "# OAuth 2.0 Authentication\\n\\nTokens expire in 3600s..."
}`}
                    </pre>
                    <div className="text-cyan/40 text-[11px]">
                      ✓ Ready for LangChain, LlamaIndex &amp; ChromaDB ingest.
                    </div>
                  </div>
                )}

                {activeTab === 'mcp-stdio' && (
                  <div className="space-y-2 text-cyan/30 animate-fadeIn">
                    <div className="text-cyan/40 font-bold">// FastMCP v2 stdio Tool Call:</div>
                    <pre className="text-[11px] text-cyan/40 bg-black/40 p-3 rounded border border-border/60 overflow-x-auto">
{`$ docharvest mcp
> Call: search_docs(query="OAuth token refresh", domain="openalgo")
> Result (189 tokens):
  OAuth 2.0 Token Refresh: POST to /oauth/token with client_credentials.
  Tokens valid for 3600s.`}
                    </pre>
                    <div className="text-cyan/40 text-[11px]">
                      ✓ 10 FastMCP tools connected to Cursor / Claude Code.
                    </div>
                  </div>
                )}
              </div>

              {/* Terminal Footer Status Bar */}
              <div className="flex items-center justify-between px-4 py-2 border-t border-border/60 bg-card/95 font-mono text-[10px] text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-cyan/40" />
                  <span>STATUS: 364/364 HARVESTED</span>
                </div>
                <span>TIME: 18.2s (20.0 pgs/sec)</span>
              </div>

            </motion.div>
          </div>

        </div>
      </div>
    </section>
  );
}
