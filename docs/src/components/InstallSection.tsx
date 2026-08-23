import React, { useState } from "react"
import { Download, Terminal, Check, Copy, Box, Apple, Laptop, Sparkles, ExternalLink } from "lucide-react"

export const InstallSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"pip" | "uvx" | "binary" | "docker">("pip")
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null)

  const handleCopy = (cmd: string, id: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedCmd(id)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  const installMethods = {
    pip: {
      title: "Python Package Manager (pip)",
      desc: "Install the CLI and Python SDK into your active virtual environment:",
      command: "pip install gitbook-downloader",
      subcommand: "gitbook-dl capture https://docs.openalgo.in/",
      details: "Requires Python 3.10 or higher. Cross-platform support for Windows, macOS, and Linux."
    },
    uvx: {
      title: "Zero-Install Instant Runner (uvx)",
      desc: "Run DocHarvest instantly without installing anything into your global Python environment:",
      command: "uvx docharvest capture https://docs.openalgo.in/ --export jsonl,pdf",
      subcommand: "uvx docharvest mcp",
      details: "Powered by Astral's ultra-fast uv tool runner. Automatic binary caching."
    },
    binary: {
      title: "Standalone Desktop GUI & CLI Binaries",
      desc: "Pre-compiled single-file binaries with zero external Python or C-dependencies:",
      command: "# Download latest GitHub Release binary",
      subcommand: "curl -LO https://github.com/RohannShetty/gitbook-downloader/releases/latest/download/docharvest-windows-x64.exe",
      details: "Includes React 18 Desktop GUI + PyWebView native shell. Windows .exe, macOS .dmg, Linux .AppImage."
    },
    docker: {
      title: "Containerized Engine (Docker)",
      desc: "Run DocHarvest in isolated, air-gapped CI/CD pipelines or homelab servers:",
      command: "docker run --rm -v $(pwd)/harvested:/data ghcr.io/rohannshetty/docharvest:latest capture https://docs.openalgo.in/",
      subcommand: "",
      details: "Lightweight Alpine-based container image under 65MB."
    }
  }

  const current = installMethods[activeTab]

  return (
    <section id="install" className="py-24 relative bg-[#0c0c10]">
      {/* Top divider */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold mb-4">
            <Download className="w-3.5 h-3.5" />
            <span>GET STARTED IN SECONDS</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Choose Your Installation Method
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            Install via your favorite package manager or download standalone binaries for Windows, macOS, and Linux.
          </p>
        </div>

        {/* Install Box */}
        <div className="max-w-4xl mx-auto rounded-2xl bg-zinc-900 border border-zinc-800 overflow-hidden shadow-2xl">
          {/* Method Tabs */}
          <div className="p-4 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center gap-2">
            {[
              { id: "pip", label: "pip install" },
              { id: "uvx", label: "uvx (Zero-Install)" },
              { id: "binary", label: "Standalone Binaries" },
              { id: "docker", label: "Docker Image" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all ${
                  activeTab === tab.id
                    ? "bg-cyan-500 text-zinc-950 font-bold shadow-md shadow-cyan-500/20"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6 sm:p-8 space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white mb-1">{current.title}</h3>
              <p className="text-xs text-zinc-400">{current.desc}</p>
            </div>

            {/* Command Box 1 */}
            <div className="relative rounded-xl bg-zinc-950 border border-zinc-800 p-4 font-mono text-xs sm:text-sm text-zinc-200 flex items-center justify-between gap-4">
              <span className="text-cyan-300 truncate select-all">{current.command}</span>
              <button
                onClick={() => handleCopy(current.command, "cmd1")}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-300 hover:text-white shrink-0"
              >
                {copiedCmd === "cmd1" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-zinc-400" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>

            {/* Subcommand if applicable */}
            {current.subcommand && (
              <div className="relative rounded-xl bg-zinc-950/70 border border-zinc-800/80 p-4 font-mono text-xs sm:text-sm text-zinc-300 flex items-center justify-between gap-4">
                <span className="truncate select-all text-zinc-300">{current.subcommand}</span>
                <button
                  onClick={() => handleCopy(current.subcommand, "cmd2")}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-300 hover:text-white shrink-0"
                >
                  {copiedCmd === "cmd2" ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-zinc-400" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Binary Download Direct Links if on binary tab */}
            {activeTab === "binary" && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-cyan-500/50 text-xs font-semibold text-zinc-200 hover:text-white transition-colors"
                >
                  <Laptop className="w-4 h-4 text-cyan-400" />
                  <span>Windows (.exe)</span>
                </a>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-indigo-500/50 text-xs font-semibold text-zinc-200 hover:text-white transition-colors"
                >
                  <Apple className="w-4 h-4 text-indigo-400" />
                  <span>macOS (.dmg)</span>
                </a>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases/latest"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 p-3 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-emerald-500/50 text-xs font-semibold text-zinc-200 hover:text-white transition-colors"
                >
                  <Box className="w-4 h-4 text-emerald-400" />
                  <span>Linux (.AppImage)</span>
                </a>
              </div>
            )}

            {/* Details Footer */}
            <div className="pt-2 text-xs text-zinc-400 font-mono">
              <span className="text-zinc-500">• </span>
              {current.details}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
