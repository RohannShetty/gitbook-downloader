'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Database, FileCode, Search, Copy, Check, Sparkles } from 'lucide-react';

const PREVIEWS = {
  markdown: {
    filename: "docs.openalgo.in/book.md",
    language: "markdown",
    code: `---
title: "OpenAlgo v2.0 Complete Developer Handbook"
source_domain: "docs.openalgo.in"
harvest_timestamp: "2026-08-23T16:42:19Z"
total_pages: 364
generator: "DocHarvest v11.0.2"
---

# Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [OAuth 2.0 Authentication](#2-oauth-20-authentication)
3. [Order Execution API](#3-order-execution-api)
4. [WebSocket Market Data Feed](#4-websocket-market-data-feed)

---

# 1. Architecture Overview
OpenAlgo operates as an ultra-low latency execution broker wrapper...`
  },
  rag: {
    filename: "exports/openalgo_rag.jsonl",
    language: "json",
    code: `{"id":"openalgo_001","source_url":"https://docs.openalgo.in/auth","title":"OAuth 2.0 Auth","content_hash":"sha256-e3b0c44...","tokens":412,"hierarchy":["API Reference","Authentication"],"chunk_text":"# OAuth 2.0 Authentication\\n\\nAccess tokens expire in 3600s..."}
{"id":"openalgo_002","source_url":"https://docs.openalgo.in/orders","title":"Place Order","content_hash":"sha256-a1b2c3d...","tokens":580,"hierarchy":["API Reference","Orders"],"chunk_text":"# Place Order POST /api/v2/orders\\n\\nDispatches an order..."}`
  },
  llmstxt: {
    filename: "docs.openalgo.in/llms.txt",
    language: "markdown",
    code: `# OpenAlgo API Documentation
> High-performance Python algorithmic trading and broker execution platform.

## Core Documentation
- [Quickstart Guide](https://docs.openalgo.in/quickstart): 5-minute local broker setup.
- [Authentication](https://docs.openalgo.in/auth): OAuth 2.0 token grant and HMAC keys.
- [Order Dispatch](https://docs.openalgo.in/orders): Limit, market, and stop-loss execution.

## Optional Reference
- [ZeroMQ Queue Architecture](https://docs.openalgo.in/arch/zeromq): Low-latency internal queue spec.`
  },
  fts5: {
    filename: "search.db (SQLite FTS5 BM25)",
    language: "sql",
    code: `-- SQLite FTS5 Full-Text Search Schema
CREATE VIRTUAL TABLE pages_fts USING fts5(
  title,
  content,
  url UNINDEXED,
  domain UNINDEXED,
  tokenize = 'porter unicode61'
);

-- Instant BM25 query in < 15ms across 1,000 pages:
SELECT url, title, snippet(pages_fts, 1, '<b>', '</b>', '...', 24) AS match_snippet
FROM pages_fts
WHERE pages_fts MATCH 'ZeroMQ retry timeout'
ORDER BY rank;`
  }
};

export function ExportStudioPreview() {
  const [activeTab, setActiveTab] = useState<keyof typeof PREVIEWS>('markdown');
  const [copied, setCopied] = useState(false);

  const current = PREVIEWS[activeTab];

  const handleCopy = () => {
    navigator.clipboard.writeText(current.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="studio" className="border-b border-border bg-card/20 py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              Export Studio Inspection
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Inspect the Generated Compilation Artifacts
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Switch between raw generated artifacts to see how DocHarvest formats Markdown, vector JSONL, <code className="text-cyan font-bold">llms.txt</code>, and SQLite FTS5 indices.
          </p>
        </div>

        {/* Studio Window Card */}
        <div className="border border/80 rounded-xl bg/95 shadow-2xl overflow-hidden">
          
          {/* Studio Navigation Bar */}
          <div className="flex flex-wrap items-center justify-between px-4 py-3 border-b border/80 bg/90 gap-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('markdown')}
                role="tab"
                aria-selected={activeTab === 'markdown'}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-semibold cursor-pointer focus-visible:outline-2 focus-visible:outline-primary transition-all ${
                  activeTab === 'markdown'
                    ? 'bg-primary/20 text-primary border border-primary/40'
                    : 'text/40 hover:text-white hover:bg/80'
                }`}
              >
                <FileText className="h-3.5 w-3.5" />
                <span>book.md</span>
              </button>

              <button
                onClick={() => setActiveTab('rag')}
                role="tab"
                aria-selected={activeTab === 'rag'}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-semibold cursor-pointer focus-visible:outline-2 focus-visible:outline-primary transition-all ${
                  activeTab === 'rag'
                    ? 'bg-primary/20 text-primary border border-primary/40'
                    : 'text/40 hover:text-white hover:bg/80'
                }`}
              >
                <Database className="h-3.5 w-3.5" />
                <span>dataset.jsonl</span>
              </button>

              <button
                onClick={() => setActiveTab('llmstxt')}
                role="tab"
                aria-selected={activeTab === 'llmstxt'}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-semibold cursor-pointer focus-visible:outline-2 focus-visible:outline-primary transition-all ${
                  activeTab === 'llmstxt'
                    ? 'bg-primary/20 text-primary border border-primary/40'
                    : 'text/40 hover:text-white hover:bg/80'
                }`}
              >
                <FileCode className="h-3.5 w-3.5" />
                <span>llms.txt</span>
              </button>

              <button
                onClick={() => setActiveTab('fts5')}
                role="tab"
                aria-selected={activeTab === 'fts5'}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-semibold cursor-pointer focus-visible:outline-2 focus-visible:outline-primary transition-all ${
                  activeTab === 'fts5'
                    ? 'bg-primary/20 text-primary border border-primary/40'
                    : 'text/40 hover:text-white hover:bg/80'
                }`}
              >
                <Search className="h-3.5 w-3.5" />
                <span>search.db (FTS5)</span>
              </button>
            </div>

            {/* Copy Artifact CTA */}
            <div className="flex items-center gap-3">
              <span className="hidden sm:inline-block font-mono text-[10px] text/40">
                {current.filename}
              </span>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border border/70 bg/80 text-xs font-mono text/20 hover:text-white hover:border-primary/60 transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary"
                aria-label="Copy sample code"
              >
                {copied ? <Check className="h-3.5 w-3.5 text/40" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copied ? 'Copied' : 'Copy Sample'}</span>
              </button>
            </div>
          </div>

          {/* Code Viewer Panel */}
          <div className="p-5 overflow-x-auto font-mono text-xs leading-relaxed bg/95">
            <pre className="!bg-transparent !p-0 !border-0 text/10">
              <code>{current.code}</code>
            </pre>
          </div>

          {/* Studio Footer */}
          <div className="flex items-center justify-between px-4 py-2.5 border-t border/80 bg/90 font-mono text-[10px] text/40">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg/40" />
              <span>SYNTAX: {current.language.toUpperCase()}</span>
            </div>
            <span>ZERO CLIENT OVERHEAD</span>
          </div>

        </div>

      </div>
    </section>
  );
}
