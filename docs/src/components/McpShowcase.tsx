import React, { useState } from "react"
import { Cpu, Check, Copy, Sparkles, Terminal, ArrowRight, ShieldCheck, Layers } from "lucide-react"

export const McpShowcase: React.FC = () => {
  const [configTarget, setConfigTarget] = useState<"cursor" | "claude">("cursor")
  const [copied, setCopied] = useState(false)

  const cursorConfig = JSON.stringify(
    {
      mcpServers: {
        docharvest: {
          command: "uvx",
          args: ["docharvest", "mcp"]
        }
      }
    },
    null,
    2
  )

  const claudeConfig = JSON.stringify(
    {
      mcpServers: {
        docharvest: {
          command: "python",
          args: ["-m", "gitbook_downloader", "mcp"]
        }
      }
    },
    null,
    2
  )

  const activeSnippet = configTarget === "cursor" ? cursorConfig : claudeConfig

  const handleCopy = () => {
    navigator.clipboard.writeText(activeSnippet)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const mcpTools = [
    { name: "download_docs", desc: "Harvest an entire documentation website into clean markdown" },
    { name: "search_docs", desc: "Execute BM25 token searches across local SQLite FTS5 index" },
    { name: "read_doc_page", desc: "Read a specific captured documentation page with frontmatter" },
    { name: "list_docs", desc: "List all indexed documentation domains and page counts" },
    { name: "get_doc_tree", desc: "Retrieve the hierarchical table of contents for a doc library" },
    { name: "diff_versions", desc: "Generate unified diffs between two harvested snapshots" },
    { name: "export_format", desc: "Export captured library to JSONL, PDF, or Markdown book" },
    { name: "status", desc: "Check current crawler background worker jobs and cache status" },
  ]

  return (
    <section id="mcp" className="py-24 relative bg-[#09090b]">
      {/* Top divider */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono font-semibold mb-4">
            <Cpu className="w-3.5 h-3.5" />
            <span>MODEL CONTEXT PROTOCOL</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Autonomous FastMCP Server for Coding Agents
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            Connect DocHarvest directly to Cursor, Claude Code, and Windsurf via standard MCP. Your AI agent can autonomously discover, harvest, and query up-to-date documentation on demand.
          </p>
        </div>

        {/* 2-Column Grid: Config Generator & 8 Tools List */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: 1-Click Config Generator */}
          <div className="lg:col-span-6 rounded-2xl bg-zinc-900/90 border border-zinc-800 p-6 sm:p-8 space-y-6 shadow-2xl">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">1-Click Agent Configuration</h3>
              <p className="text-xs text-zinc-400">
                Add this configuration to your IDE's MCP settings file to enable autonomous documentation harvesting:
              </p>
            </div>

            {/* Target Switcher */}
            <div className="flex items-center gap-2 bg-zinc-950 p-1 rounded-xl border border-zinc-800 w-fit">
              <button
                onClick={() => setConfigTarget("cursor")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  configTarget === "cursor"
                    ? "bg-indigo-500 text-white font-bold shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Cursor (.cursor/mcp.json)
              </button>

              <button
                onClick={() => setConfigTarget("claude")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  configTarget === "claude"
                    ? "bg-indigo-500 text-white font-bold shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Claude Desktop
              </button>
            </div>

            {/* JSON Code Box */}
            <div className="relative rounded-xl bg-zinc-950 border border-zinc-800 overflow-hidden">
              <div className="p-3 bg-[#111116] border-b border-zinc-800 flex items-center justify-between">
                <span className="text-xs font-mono text-zinc-400">
                  {configTarget === "cursor" ? ".cursor/mcp.json" : "claude_desktop_config.json"}
                </span>

                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3 py-1 rounded bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-300 hover:text-white"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-zinc-400" />
                      <span>Copy Config</span>
                    </>
                  )}
                </button>
              </div>

              <div className="p-4 font-mono text-xs text-zinc-200 bg-[#09090c] select-text">
                <pre>{activeSnippet}</pre>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 text-xs text-zinc-400 space-y-1.5">
              <div className="font-semibold text-zinc-200 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Zero Installation Required with \`uvx\`</span>
              </div>
              <p>
                When using Cursor with <code className="text-cyan-300">uvx docharvest mcp</code>, uv automatically downloads and runs the latest isolated binary on demand.
              </p>
            </div>
          </div>

          {/* Right Column: 8 Native MCP Tools List */}
          <div className="lg:col-span-6 rounded-2xl bg-zinc-900/90 border border-zinc-800 p-6 sm:p-8 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-white">8 Native FastMCP Tools</h3>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                stdio JSON-RPC
              </span>
            </div>
            <p className="text-xs text-zinc-400 mb-4">
              Your AI coding assistant gains full programmatic control over documentation capture and search:
            </p>

            <div className="space-y-2.5">
              {mcpTools.map((tool, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-zinc-950/70 border border-zinc-800 flex items-start gap-3 hover:border-indigo-500/40 transition-colors"
                >
                  <code className="text-xs font-mono font-semibold text-cyan-300 shrink-0 mt-0.5">
                    {tool.name}()
                  </code>
                  <span className="text-xs text-zinc-400 leading-relaxed">
                    {tool.desc}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
