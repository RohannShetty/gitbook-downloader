import React, { useState } from "react"
import { OUTPUT_CONTRACT_ITEMS, FourPartContractItem } from "../data/showcaseData"
import { FolderTree, FileText, BookOpen, Layers, Check, Copy, Sparkles, ShieldCheck } from "lucide-react"

export const OutputContract: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<FourPartContractItem>(OUTPUT_CONTRACT_ITEMS[0])
  const [copied, setCopied] = useState(false)

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="contract" className="py-24 relative bg-[#0d0d12]">
      {/* Background divider */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono font-semibold mb-4">
            <FolderTree className="w-3.5 h-3.5" />
            <span>DETERMINISTIC KNOWLEDGE CORPUS</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            The Four-Part Output Contract
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            Every capture produces four structured, deterministic artifacts. No messy scrapings, no unpredictable directories — just pure, engineered knowledge ready for LLMs, offline readers, and search indices.
          </p>
        </div>

        {/* Interactive 4-Part Explorer Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: 4-Item Selector Cards */}
          <div className="lg:col-span-5 space-y-3">
            {OUTPUT_CONTRACT_ITEMS.map((item) => {
              const isSelected = selectedItem.id === item.id
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-5 rounded-2xl border cursor-pointer transition-all duration-200 ${
                    isSelected
                      ? "bg-zinc-900 border-cyan-400/60 shadow-xl shadow-cyan-950/20 scale-[1.01]"
                      : "bg-zinc-950/70 border-zinc-800 hover:bg-zinc-900/60 hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-base text-zinc-100">{item.title}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[11px] font-mono border ${item.color}`}>
                      {item.badge}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-cyan-300/90 mb-2">
                    <code>{item.path}</code>
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              )
            })}
          </div>

          {/* Right Column: Code & Artifact Inspector */}
          <div className="lg:col-span-7 rounded-2xl bg-zinc-900 border border-zinc-800 overflow-hidden shadow-2xl">
            {/* Inspector Header */}
            <div className="p-4 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
                <span className="font-mono text-xs text-zinc-300 font-semibold">
                  {selectedItem.path}
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                  {selectedItem.fileType}
                </span>
              </div>

              {/* Copy Artifact Content */}
              <button
                onClick={() => handleCopy(selectedItem.snippet)}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-zinc-900 border border-zinc-700/80 text-xs font-mono text-zinc-300 hover:text-white transition-all shadow-sm"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-zinc-400" />
                    <span>Copy Content</span>
                  </>
                )}
              </button>
            </div>

            {/* Code Screen */}
            <div className="p-6 bg-[#0a0a0e] font-mono text-xs sm:text-sm text-zinc-200 overflow-x-auto min-h-[380px] select-text">
              <pre className="leading-relaxed whitespace-pre-wrap selection:bg-cyan-500/30">
                {selectedItem.snippet}
              </pre>
            </div>

            {/* Inspector Footer */}
            <div className="p-4 bg-zinc-950/90 border-t border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-zinc-400 font-mono">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <span>Deterministic hashing • Verified provenance</span>
              </div>
              <span className="text-zinc-500">Zero duplicate headers</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
