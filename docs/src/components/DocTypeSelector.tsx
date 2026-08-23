import React, { useState } from "react"
import { DOC_FRAMEWORKS, DocFramework } from "../data/showcaseData"
import { Check, Copy, FileCode, Globe, ShieldAlert, Sparkles, Layers, Search, ArrowRight } from "lucide-react"

export const DocTypeSelector: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState<DocFramework>(DOC_FRAMEWORKS[0])
  const [previewTab, setPreviewTab] = useState<"clean" | "raw">("clean")
  const [copied, setCopied] = useState(false)
  const [customUrl, setCustomUrl] = useState("")
  const [customDetected, setCustomDetected] = useState<DocFramework | null>(null)

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSimulateDetect = (url: string) => {
    setCustomUrl(url)
    const lower = url.toLowerCase()
    if (lower.includes("gitbook") || lower.includes("openalgo")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "gitbook") || null)
    } else if (lower.includes("mintlify")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "mintlify") || null)
    } else if (lower.includes("docusaurus") || lower.includes("react")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "docusaurus") || null)
    } else if (lower.includes("nextra") || lower.includes("nextjs") || lower.includes("turborepo")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "nextra") || null)
    } else if (lower.includes("readme")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "readme") || null)
    } else if (lower.includes("vitepress") || lower.includes("vue") || lower.includes("mkdocs")) {
      setCustomDetected(DOC_FRAMEWORKS.find((f) => f.id === "vitepress") || null)
    } else {
      setCustomDetected(DOC_FRAMEWORKS[0])
    }
  }

  return (
    <section id="frameworks" className="py-24 relative bg-[#09090b]">
      {/* Background divider line with gradient */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold mb-4">
            <Globe className="w-3.5 h-3.5" />
            <span>PLATFORM-AWARE EXTRACTION</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Universal Documentation Engine
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            Different documentation platforms use wildly different architectures. DocHarvest automatically detects the framework, bypasses HTML wrappers, and extracts pristine markdown directly from source endpoints.
          </p>
        </div>

        {/* Framework Selector Tabs */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 mb-10">
          {DOC_FRAMEWORKS.map((framework) => {
            const isSelected = selectedFramework.id === framework.id
            return (
              <button
                key={framework.id}
                onClick={() => setSelectedFramework(framework)}
                className={`p-3.5 rounded-xl border text-left transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? "bg-zinc-900 border-cyan-400/60 shadow-lg shadow-cyan-950/30 scale-[1.02]"
                    : "bg-zinc-950/60 border-zinc-800/80 hover:bg-zinc-900/60 hover:border-zinc-700"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-sm text-zinc-100">{framework.name}</span>
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isSelected ? "bg-cyan-400 animate-pulse" : "bg-zinc-700"
                      }`}
                    />
                  </div>
                  <div className="text-[11px] font-mono text-zinc-400 truncate">
                    Score: {framework.detectionPriority}/100
                  </div>
                </div>
                <div className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-cyan-400/90 truncate">
                  {framework.badge}
                </div>
              </button>
            )
          })}
        </div>

        {/* Active Framework Details & Side-by-Side Comparison Box */}
        <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden shadow-2xl">
          {/* Framework Header Banner */}
          <div className="p-6 sm:p-8 bg-zinc-900 border-b border-zinc-800 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-2xl font-bold text-white font-mono">
                  {selectedFramework.name} Extractor
                </h3>
                <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-medium">
                  {selectedFramework.badge}
                </span>
                <span className="text-xs font-mono text-zinc-400">
                  Priority: {selectedFramework.detectionPriority}/100
                </span>
              </div>
              <p className="text-sm text-zinc-300 max-w-3xl leading-relaxed">
                {selectedFramework.description}
              </p>
              <div className="text-xs font-mono text-zinc-400 flex items-center gap-1.5 pt-1">
                <span className="text-cyan-400 font-semibold">Heuristic match:</span>
                <code className="bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800 text-zinc-300">
                  {selectedFramework.heuristicMatch}
                </code>
              </div>
            </div>

            {/* Features Checklist */}
            <div className="bg-zinc-950/80 p-4 rounded-xl border border-zinc-800 lg:w-96 shrink-0 space-y-2">
              <div className="text-xs font-semibold text-zinc-200 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Specialized Capabilities</span>
              </div>
              {selectedFramework.features.map((feat, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-zinc-300">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive URL Simulator Bar */}
          <div className="px-6 py-3 bg-[#111116] border-b border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 flex-1">
              <span className="font-mono text-zinc-400">Target Sample URL:</span>
              <code className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-700 text-cyan-300 font-mono flex-1 truncate">
                {selectedFramework.sampleUrl}
              </code>
            </div>

            {/* View Switcher Tabs (Clean Markdown vs Raw Wget Soup) */}
            <div className="flex items-center gap-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800 self-start sm:self-auto">
              <button
                onClick={() => setPreviewTab("clean")}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${
                  previewTab === "clean"
                    ? "bg-cyan-500 text-zinc-950 font-bold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                <FileCode className="w-3.5 h-3.5" />
                <span>DocHarvest Clean Markdown</span>
              </button>
              <button
                onClick={() => setPreviewTab("raw")}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${
                  previewTab === "raw"
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                <span>Raw Wget / HTML Soup</span>
              </button>
            </div>
          </div>

          {/* Code Viewer Panel */}
          <div className="relative bg-[#0c0c10] p-6 font-mono text-xs sm:text-sm overflow-x-auto min-h-[300px]">
            {/* Copy Button */}
            <button
              onClick={() =>
                handleCopy(
                  previewTab === "clean"
                    ? selectedFramework.cleanMarkdownSnippet
                    : selectedFramework.rawHtmlSnippet
                )
              }
              className="absolute top-4 right-4 z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900/90 border border-zinc-700/80 text-xs font-mono text-zinc-300 hover:text-white transition-all shadow-md"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Copy Code</span>
                </>
              )}
            </button>

            {previewTab === "clean" ? (
              <div className="space-y-1">
                <div className="text-xs text-emerald-400 mb-2 font-mono flex items-center gap-1.5">
                  <Check className="w-4 h-4" />
                  <span>Zero HTML Noise • Cryptographic SHA-256 Frontmatter • Intact Syntax Blocks</span>
                </div>
                <pre className="text-zinc-200 leading-relaxed whitespace-pre-wrap selection:bg-cyan-500/30">
                  {selectedFramework.cleanMarkdownSnippet}
                </pre>
              </div>
            ) : (
              <div className="space-y-1">
                <div className="text-xs text-rose-400 mb-2 font-mono flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Notice: 40KB+ of cookie divs, search modals, and broken relative links that waste LLM tokens.</span>
                </div>
                <pre className="text-zinc-400 leading-relaxed whitespace-pre-wrap selection:bg-rose-500/30">
                  {selectedFramework.rawHtmlSnippet}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Interactive Custom URL Simulator Bar */}
        <div className="mt-8 p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <Search className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="text-xs font-medium text-zinc-300 shrink-0">Test Custom URL Heuristic:</span>
            <input
              type="text"
              placeholder="e.g. https://docs.openalgo.in, https://mintlify.com/docs, https://react.dev"
              value={customUrl}
              onChange={(e) => handleSimulateDetect(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-700/80 rounded-lg px-3 py-1.5 text-xs font-mono text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {customDetected && (
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-zinc-400">Detected:</span>
              <span className="px-2 py-1 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-semibold">
                {customDetected.name}
              </span>
              <button
                onClick={() => setSelectedFramework(customDetected)}
                className="px-2.5 py-1 rounded bg-zinc-800 text-zinc-200 hover:text-white transition-colors"
              >
                Inspect
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
