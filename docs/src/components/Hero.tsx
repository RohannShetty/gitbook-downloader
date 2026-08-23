import React, { useState } from "react"
import { Terminal, Download, Sparkles, Check, Copy, ArrowRight, ShieldCheck, Cpu, BookOpen, Layers } from "lucide-react"
import { TerminalHero } from "./TerminalHero"

interface HeroProps {
  onOpenInstallModal: () => void
}

export const Hero: React.FC<HeroProps> = ({ onOpenInstallModal }) => {
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null)
  const [activeInstallTab, setActiveInstallTab] = useState<"pip" | "uvx">("pip")

  const copyCommand = (cmd: string, id: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedCmd(id)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  return (
    <section className="relative pt-32 pb-20 overflow-hidden text-center">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] sm:w-[900px] h-[450px] bg-gradient-to-tr from-cyan-500/15 via-indigo-600/10 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-10 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-40 right-10 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Release Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-zinc-900/90 border border-zinc-700/80 text-xs text-zinc-300 mb-8 backdrop-blur-md hover:border-cyan-500/50 transition-all cursor-default shadow-lg shadow-cyan-950/20">
          <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-semibold text-cyan-300">DocHarvest v10.0.1 Released</span>
          <span className="text-zinc-600">•</span>
          <span className="text-zinc-400">Universal AST Engine &amp; FastMCP Server</span>
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        </div>

        {/* Main Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-5xl mx-auto leading-[1.1] mb-6">
          Turn Any Documentation Site into{" "}
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
            LLM-Ready Markdown
          </span>
          , Vector Context &amp; Offline Books.
        </h1>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl text-zinc-300 max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
          The universal documentation compiler for AI engineers, offline developers, and DevOps teams.
          Auto-detects <span className="text-cyan-300 font-medium">GitBook</span>, <span className="text-emerald-300 font-medium">Mintlify</span>, <span className="text-indigo-300 font-medium">Docusaurus</span>, <span className="text-purple-300 font-medium">Nextra</span>, <span className="text-amber-300 font-medium">ReadMe</span>, and <span className="text-sky-300 font-medium">VitePress</span>. Captures pristine source markdown with zero HTML noise.
        </p>

        {/* Interactive 1-Click Install Command Pill */}
        <div className="max-w-xl mx-auto mb-10">
          <div className="p-1.5 rounded-2xl bg-zinc-900/90 border border-zinc-700/90 backdrop-blur-xl shadow-2xl flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
            {/* Tabs (pip vs uvx) */}
            <div className="flex items-center gap-1 bg-zinc-950/80 p-1 rounded-xl border border-zinc-800 self-center sm:self-auto">
              <button
                onClick={() => setActiveInstallTab("pip")}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
                  activeInstallTab === "pip"
                    ? "bg-cyan-500 text-zinc-950 font-bold shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                pip
              </button>
              <button
                onClick={() => setActiveInstallTab("uvx")}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
                  activeInstallTab === "uvx"
                    ? "bg-cyan-500 text-zinc-950 font-bold shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                uvx
              </button>
            </div>

            {/* Command Text */}
            <div className="flex-1 px-3 text-left font-mono text-xs sm:text-sm text-zinc-200 truncate">
              {activeInstallTab === "pip" ? (
                <span>
                  <span className="text-cyan-400 select-none">$ </span>pip install gitbook-downloader
                </span>
              ) : (
                <span>
                  <span className="text-cyan-400 select-none">$ </span>uvx docharvest capture &lt;url&gt;
                </span>
              )}
            </div>

            {/* Copy Button */}
            <button
              onClick={() =>
                copyCommand(
                  activeInstallTab === "pip"
                    ? "pip install gitbook-downloader"
                    : "uvx docharvest capture https://docs.openalgo.in/",
                  activeInstallTab
                )
              }
              className="flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white text-xs font-semibold font-mono transition-all active:scale-95"
            >
              {copiedCmd === activeInstallTab ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
          <button
            onClick={onOpenInstallModal}
            className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-zinc-950 font-bold text-sm transition-all shadow-xl shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]"
          >
            <Download className="w-4 h-4" />
            <span>Download Desktop App &amp; CLI</span>
          </button>

          <a
            href="#mcp"
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800/90 border border-zinc-700/80 text-zinc-200 hover:text-white font-semibold text-sm transition-all hover:border-indigo-500/50 hover:scale-[1.02] active:scale-[0.98]"
          >
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span>Connect FastMCP to Cursor</span>
            <ArrowRight className="w-4 h-4 text-zinc-500" />
          </a>
        </div>

        {/* Live Terminal Emulator Component */}
        <TerminalHero />

        {/* Bottom Feature Badges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mt-14">
          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-left">
            <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0" />
            <div>
              <div className="text-xs font-semibold text-zinc-200">100% Local &amp; Private</div>
              <div className="text-[11px] text-zinc-400">Zero cloud API keys or telemetry</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-left">
            <Layers className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="text-xs font-semibold text-zinc-200">AST Header Splitter</div>
              <div className="text-[11px] text-zinc-400">Never splits code blocks or lines</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-left">
            <BookOpen className="w-5 h-5 text-indigo-400 shrink-0" />
            <div>
              <div className="text-xs font-semibold text-zinc-200">Pure-Python PDF</div>
              <div className="text-[11px] text-zinc-400">Built-in fpdf2, zero C-libraries</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-left">
            <Cpu className="w-5 h-5 text-amber-400 shrink-0" />
            <div>
              <div className="text-xs font-semibold text-zinc-200">Native FastMCP Server</div>
              <div className="text-[11px] text-zinc-400">8 tools for Cursor &amp; Claude Code</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
