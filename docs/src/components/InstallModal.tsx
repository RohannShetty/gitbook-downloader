import React, { useState } from "react"
import { X, Terminal, Check, Copy, Download, Box, Apple, Laptop, Cpu } from "lucide-react"

interface InstallModalProps {
  isOpen: boolean
  onClose: () => void
}

export const InstallModal: React.FC<InstallModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<"pip" | "uvx" | "desktop" | "mcp">("pip")
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null)

  if (!isOpen) return null

  const handleCopy = (cmd: string, id: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedCmd(id)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden text-left">
        {/* Header */}
        <div className="p-5 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Get Started with DocHarvest</h3>
              <p className="text-xs text-zinc-400">Choose your preferred installation method</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Selection */}
        <div className="p-4 bg-zinc-950/60 border-b border-zinc-800/80 flex flex-wrap gap-2">
          {[
            { id: "pip", label: "pip (Python)" },
            { id: "uvx", label: "uvx (Instant)" },
            { id: "desktop", label: "Desktop GUI App" },
            { id: "mcp", label: "FastMCP Server" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-cyan-500 text-zinc-950 font-bold shadow"
                  : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 font-mono text-xs">
          {activeTab === "pip" && (
            <div className="space-y-3">
              <p className="text-zinc-400 font-sans text-xs">
                Install DocHarvest globally or in your virtual environment using pip:
              </p>
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-200">
                <code className="text-cyan-300 select-all">pip install gitbook-downloader</code>
                <button
                  onClick={() => handleCopy("pip install gitbook-downloader", "pip")}
                  className="flex items-center gap-1 px-3 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white"
                >
                  {copiedCmd === "pip" ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCmd === "pip" ? "Copied" : "Copy"}</span>
                </button>
              </div>
              <p className="text-[11px] text-zinc-500 font-sans">
                Then run: <code className="text-zinc-300 font-mono">gitbook-dl capture https://docs.openalgo.in/</code>
              </p>
            </div>
          )}

          {activeTab === "uvx" && (
            <div className="space-y-3">
              <p className="text-zinc-400 font-sans text-xs">
                Run DocHarvest without modifying your local environment via Astral's uvx:
              </p>
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-200">
                <code className="text-cyan-300 select-all">uvx docharvest capture https://docs.openalgo.in/ --export jsonl,pdf</code>
                <button
                  onClick={() => handleCopy("uvx docharvest capture https://docs.openalgo.in/ --export jsonl,pdf", "uvx")}
                  className="flex items-center gap-1 px-3 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white"
                >
                  {copiedCmd === "uvx" ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCmd === "uvx" ? "Copied" : "Copy"}</span>
                </button>
              </div>
            </div>
          )}

          {activeTab === "desktop" && (
            <div className="space-y-3">
              <p className="text-zinc-400 font-sans text-xs">
                Download zero-dependency standalone executable binaries from GitHub Releases:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-cyan-500/50 flex items-center justify-center gap-2 text-zinc-200 font-sans font-semibold"
                >
                  <Laptop className="w-4 h-4 text-cyan-400" />
                  <span>Windows .exe</span>
                </a>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-indigo-500/50 flex items-center justify-center gap-2 text-zinc-200 font-sans font-semibold"
                >
                  <Apple className="w-4 h-4 text-indigo-400" />
                  <span>macOS .dmg</span>
                </a>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-emerald-500/50 flex items-center justify-center gap-2 text-zinc-200 font-sans font-semibold"
                >
                  <Box className="w-4 h-4 text-emerald-400" />
                  <span>Linux .AppImage</span>
                </a>
              </div>
            </div>
          )}

          {activeTab === "mcp" && (
            <div className="space-y-3">
              <p className="text-zinc-400 font-sans text-xs">
                Run the FastMCP server for Cursor and Claude Code:
              </p>
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-200">
                <code className="text-cyan-300 select-all">uvx docharvest mcp</code>
                <button
                  onClick={() => handleCopy("uvx docharvest mcp", "mcp")}
                  className="flex items-center gap-1 px-3 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white"
                >
                  {copiedCmd === "mcp" ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCmd === "mcp" ? "Copied" : "Copy"}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-zinc-950 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-400">
          <span>License: MIT (100% Free &amp; Open Source)</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
