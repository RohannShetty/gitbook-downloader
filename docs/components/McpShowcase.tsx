'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Terminal, Copy, Check, Sparkles, Bot, ArrowRight } from 'lucide-react';

const MCP_CONFIGS = {
  cursor: {
    title: "Cursor IDE",
    filename: ".cursor/mcp.json",
    snippet: `{
  "mcpServers": {
    "docharvest": {
      "command": "uvx",
      "args": ["gitbook-downloader", "mcp"]
    }
  }
}`
  },
  claude: {
    title: "Claude Code / Desktop",
    filename: "claude_desktop_config.json",
    snippet: `{
  "mcpServers": {
    "docharvest": {
      "command": "uv",
      "args": ["run", "docharvest", "mcp"]
    }
  }
}`
  },
  windsurf: {
    title: "Windsurf",
    filename: "~/.codeium/windsurf/mcp_config.json",
    snippet: `{
  "mcpServers": {
    "docharvest": {
      "command": "python",
      "args": ["-m", "gitbook_downloader.mcp"]
    }
  }
}`
  },
  vscode: {
    title: "VS Code (Copilot)",
    filename: ".vscode/mcp.json",
    snippet: `{
  "servers": {
    "docharvest": {
      "type": "stdio",
      "command": "uvx",
      "args": ["gitbook-downloader", "mcp"]
    }
  }
}`
  }
};

const MCP_TOOLS = [
  { name: "search_docs", desc: "BM25 ranked full-text search with token-efficient ~200 token snippets." },
  { name: "download_docs", desc: "Harvests any documentation URL into Markdown, book.md & llms.txt." },
  { name: "query_doc_graph", desc: "Non-linear semantic concept navigation and prerequisite entity graphs." },
  { name: "get_related_concepts", desc: "Retrieves symbols, API endpoints, and connected architectural concepts." },
  { name: "get_doc", desc: "Reads full compiled book.md or targeted chapter markdown." },
  { name: "list_domains", desc: "Lists all locally indexed and cached documentation portals." },
  { name: "diff_versions", desc: "Calculates unified structural diffs between two snapshot versions." },
  { name: "export_docs", desc: "Exports docset into Markdown, vector JSONL RAG chunks, or printable PDF." },
];

export function McpShowcase() {
  const [selectedClient, setSelectedClient] = useState<keyof typeof MCP_CONFIGS>('cursor');
  const [copied, setCopied] = useState(false);

  const current = MCP_CONFIGS[selectedClient];

  const handleCopy = () => {
    navigator.clipboard.writeText(current.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="mcp" className="border-b border-border bg-card/20 py-16 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-cyan/40 font-bold tracking-widest uppercase flex items-center gap-1.5">
              <Bot className="h-4 w-4 text-cyan/40" />
              <span>Model Context Protocol (FastMCP v2)</span>
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Give Cursor &amp; Claude Native Documentation Powers
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Connect DocHarvest to your AI agent via FastMCP stdio in 30 seconds. Your agent gains tools to crawl, index, and query external documentation on demand.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Config Generator */}
          <div className="lg:col-span-7 space-y-4">
            
            {/* Client Selector Buttons */}
            <div className="flex items-center gap-2">
              {Object.entries(MCP_CONFIGS).map(([key, item]) => (
                <button
                  key={key}
                  onClick={() => setSelectedClient(key as any)}
                  className={`px-3 py-1.5 rounded-lg border font-mono text-xs font-semibold transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                    selectedClient === key
                      ? 'border-border/50 bg-card/50 text-cyan font-bold'
                      : 'border-border bg-card text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {item.title}
                </button>
              ))}
            </div>

            {/* Config Snippet Card */}
            <div className="border border-border/80 rounded-xl bg-card/95 shadow-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-border/80 bg-card/90 font-mono text-[11px] text-cyan/40">
                <span className="text-cyan/40 font-bold">{current.filename}</span>
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan/80 hover:bg-primary/20 hover:text-white transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary text-xs text-cyan/20 border border-border/70"
                  aria-label="Copy MCP configuration"
                >
                  {copied ? <Check className="h-3 w-3 text-cyan/40" /> : <Copy className="h-3 w-3" />}
                  <span>{copied ? 'Copied' : 'Copy JSON'}</span>
                </button>
              </div>

              <div className="p-4 bg-card/95 font-mono text-xs leading-relaxed overflow-x-auto">
                <pre className="!bg-transparent !p-0 !border-0 text-cyan/10">
                  <code>{current.snippet}</code>
                </pre>
              </div>
            </div>

            <div className="text-[11px] font-mono text-muted-foreground">
              💡 Zero configuration needed. Once registered, ask your agent: <span className="text-foreground font-semibold">&quot;Search DocHarvest for OpenAlgo order payload schema.&quot;</span>
            </div>

          </div>

          {/* Right Column: Native Agent Tools */}
          <div className="lg:col-span-5 space-y-3">
            <div className="font-mono text-xs font-bold text-foreground uppercase tracking-wider mb-2">
              8 Available Agent Tool Endpoints:
            </div>

            <div className="space-y-2.5">
              {MCP_TOOLS.map((tool) => (
                <div key={tool.name} className="p-3.5 rounded-lg border border-border bg-card font-mono text-xs space-y-1 hover:border-border/50 transition-colors">
                  <div className="text-cyan font-bold">
                    @{tool.name}()
                  </div>
                  <div className="text-muted-foreground text-[11px]">
                    {tool.desc}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
