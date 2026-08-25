'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Download, ArrowRight, Play, Check, Copy, Sparkles, Layers, Cpu, FileText } from 'lucide-react';
import { WindowsIcon, PythonIcon } from './Icons';

interface HeroProps {
  onOpenInstallModal: () => void;
}

const TERMINAL_LOGS = [
  { text: "$ docharvest crawl https://docs.openalgo.in/v/v2.0 --rag --pdf --fast-ast", color: "text-cyan-400 font-bold" },
  { text: "⚡ [Heuristic] Detected GitBook Space engine (version selector: v2.0)", color: "text-indigo-300" },
  { text: "🔍 Discovering documentation tree via sitemap and AST BFS...", color: "text-zinc-400" },
  { text: "   ├── Discovered: /api-reference/oauth [3.2 KB raw .md]", color: "text-zinc-300" },
  { text: "   ├── Discovered: /api-reference/orders [14.8 KB raw .md]", color: "text-zinc-300" },
  { text: "   ├── Discovered: /api-reference/positions [6.1 KB raw .md]", color: "text-zinc-300" },
  { text: "   └── Discovered: /algorithms/quickstart [8.4 KB raw .md]", color: "text-zinc-300" },
  { text: "📥 Parallel AST crawl: 364 pages harvested in 18.2s (20.0 pages/sec)", color: "text-emerald-400 font-semibold" },
  { text: "📦 Compiling outputs:", color: "text-amber-300 font-medium" },
  { text: "   ├── book.md (consolidated single handbook with TOC)", color: "text-zinc-300" },
  { text: "   ├── llms.txt (standardized AI context manifest)", color: "text-zinc-300" },
  { text: "   ├── openalgo_rag.jsonl (vector chunks + SHA-256 metadata)", color: "text-zinc-300" },
  { text: "   └── openalgo_handbook.pdf (publication-grade printable PDF)", color: "text-zinc-300" },
  { text: "✨ FastMCP server listening on stdio. Ready for Cursor & Claude Code!", color: "text-cyan-300 font-bold" }
];

export function Hero({ onOpenInstallModal }: HeroProps) {
  const [copiedPip, setCopiedPip] = useState(false);
  const [activeTab, setActiveTab] = useState<'terminal' | 'ast' | 'vector'>('terminal');

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
      <div className="absolute top-1/3 right-1/4 h-[300px] w-[300px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Headline & Action CTAs */}
          <div className="lg:col-span-6 flex flex-col items-start space-y-6">
            
            {/* Version & Capability Badge */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-xs font-mono text-cyan-300"
            >
              <Sparkles className="h-3.5 w-3.5 text-cyan-400 animate-pulse" />
              <span>DocHarvest v10.0.1 — AST Compiler &amp; FastMCP</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.08] text-foreground"
            >
              Turn any documentation into <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-cyan-400 to-emerald-400">LLM-ready context</span> &amp; offline books.
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base sm:text-lg text-muted-foreground font-mono leading-relaxed"
            >
              Crawl GitBook, Mintlify, Docusaurus, Nextra, and ReadMe with AST precision. Compile clean Markdown, vector RAG JSONL, <code className="text-cyan-300">llms.txt</code>, and printable PDFs with zero HTML noise.
            </motion.p>

            {/* Primary Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-wrap items-center gap-3 pt-2 w-full"
            >
              <a
                href="https://github.com/RohannShetty/gitbook-downloader/releases/download/v10.0.1/docharvest-windows-latest.exe"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-primary px-5 text-xs font-mono font-bold text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/25 transition-all duration-200"
              >
                <WindowsIcon className="h-4 w-4" />
                <span>Download for Windows (.exe)</span>
              </a>

              <button
                onClick={onOpenInstallModal}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-border bg-card px-5 text-xs font-mono font-bold text-foreground hover:border-primary/50 hover:bg-secondary transition-all duration-200 cursor-pointer"
              >
                <Download className="h-3.5 w-3.5 text-cyan-400" />
                <span>All Platforms (CLI / GUI)</span>
              </button>
            </motion.div>

            {/* Quick Copy Terminal Snippet */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="flex items-center gap-2 w-full max-w-md p-2.5 rounded-lg border border-border bg-card/60 font-mono text-xs text-muted-foreground"
            >
              <span className="text-primary font-bold pl-1">$</span>
              <span className="flex-1 text-foreground">pip install gitbook-downloader</span>
              <button
                onClick={copyPipCommand}
                className="p-1.5 rounded-md hover:bg-secondary hover:text-foreground text-muted-foreground transition-colors cursor-pointer"
                title="Copy Command"
              >
                {copiedPip ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              </button>
            </motion.div>

            {/* Fast Heuristic Metrics */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border w-full font-mono text-xs">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase">Speed</span>
                <p className="font-bold text-emerald-400">20.0 pgs/sec</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase">Noise Redux</span>
                <p className="font-bold text-cyan-400">89% Token Cut</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase">Local AI</span>
                <p className="font-bold text-indigo-400">FastMCP Ready</p>
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
              <div className="flex items-center justify-between px-4 py-3 border-b border-border/80 bg-zinc-950/80">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 font-mono text-[11px] text-muted-foreground">
                    docharvest@terminal — v10.0.1
                  </span>
                </div>
                
                {/* Mode Selector */}
                <div className="flex items-center gap-1 font-mono text-[10px]">
                  <button
                    onClick={() => setActiveTab('terminal')}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer ${
                      activeTab === 'terminal' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Live Logs
                  </button>
                  <button
                    onClick={() => setActiveTab('ast')}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer ${
                      activeTab === 'ast' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    AST Filter
                  </button>
                  <button
                    onClick={() => setActiveTab('vector')}
                    className={`px-2 py-1 rounded transition-colors cursor-pointer ${
                      activeTab === 'vector' ? 'bg-primary/20 text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Vector JSONL
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
                  <div className="space-y-2 text-zinc-300 animate-fadeIn">
                    <div className="text-cyan-400 font-bold">// AST Heuristic Boundary Isolation:</div>
                    <pre className="text-[11px] text-zinc-400 bg-black/40 p-3 rounded border border-border/60 overflow-x-auto">
{`def extract_clean_article(soup: BeautifulSoup) -> str:
    # 1. Eliminate navigation, footers, & cookie banners
    for noise in soup.select("nav, footer, .sidebar, .cookie-banner"):
        noise.decompose()
        
    # 2. Extract structured Markdown preserving code blocks
    article = soup.find("article") or soup.find("main")
    return markdownify(str(article), heading_style="ATX")`}
                    </pre>
                    <div className="text-emerald-400 text-[11px]">
                      ✓ Extracted 364 articles with zero wrapper bloat.
                    </div>
                  </div>
                )}

                {activeTab === 'vector' && (
                  <div className="space-y-2 text-zinc-300 animate-fadeIn">
                    <div className="text-amber-400 font-bold">// RAG JSONL Vector Payload Chunk:</div>
                    <pre className="text-[11px] text-zinc-400 bg-black/40 p-3 rounded border border-border/60 overflow-x-auto">
{`{
  "id": "openalgo_oauth_v2",
  "source_url": "https://docs.openalgo.in/v/v2.0/auth",
  "title": "OAuth 2.0 Authentication",
  "content_hash": "sha256-e3b0c44...",
  "tokens": 412,
  "chunk_text": "# OAuth 2.0 Authentication\\n\\nTokens expire in 3600s..."
}`}
                    </pre>
                    <div className="text-cyan-400 text-[11px]">
                      ✓ Ready for LangChain, LlamaIndex &amp; ChromaDB ingest.
                    </div>
                  </div>
                )}
              </div>

              {/* Terminal Footer Status Bar */}
              <div className="flex items-center justify-between px-4 py-2 border-t border-border/60 bg-zinc-950 font-mono text-[10px] text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
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
