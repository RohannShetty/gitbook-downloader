import React, { useState } from "react"
import { COMPARISON_DATA, ComparisonDimension } from "../data/showcaseData"
import { Check, X, Shield, Sparkles, Filter } from "lucide-react"

export const FeatureMatrix: React.FC = () => {
  const [filterCategory, setFilterCategory] = useState<"all" | "core" | "ai" | "export" | "storage">("all")

  const filteredDimensions = COMPARISON_DATA.filter((dim) =>
    filterCategory === "all" ? true : dim.category === filterCategory
  )

  return (
    <section id="comparison" className="py-24 relative bg-[#09090b]">
      {/* Top divider */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold mb-4">
            <Shield className="w-3.5 h-3.5" />
            <span>HONEST CAPABILITY MATRIX</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            DocHarvest vs Raw Scrapers &amp; Cloud APIs
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            See how DocHarvest compares across 17 technical dimensions against curl scripts, hosted cloud scraper APIs, and generic web crawler libraries.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
          {[
            { id: "all", label: "All Dimensions (17)" },
            { id: "ai", label: "AI & RAG Preparation" },
            { id: "export", label: "Export & PDF Studio" },
            { id: "storage", label: "Storage & Concurrency" },
            { id: "core", label: "Core Engine" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterCategory(tab.id as any)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-medium transition-all ${
                filterCategory === tab.id
                  ? "bg-cyan-500 text-zinc-950 font-bold shadow-md shadow-cyan-500/20"
                  : "bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Responsive Table Container */}
        <div className="rounded-2xl bg-zinc-900/90 border border-zinc-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm font-mono">
              {/* Table Header */}
              <thead>
                <tr className="bg-zinc-950 border-b border-zinc-800 text-zinc-400">
                  <th className="py-4 px-5 font-semibold text-zinc-200 w-1/4">Capability / Dimension</th>
                  <th className="py-4 px-4 font-bold text-cyan-300 bg-cyan-950/30 border-x border-cyan-500/30 text-center w-1/4">
                    <div className="flex items-center justify-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-cyan-400" />
                      <span>DocHarvest</span>
                    </div>
                  </th>
                  <th className="py-4 px-4 font-medium text-zinc-400 text-center">curl / wget</th>
                  <th className="py-4 px-4 font-medium text-zinc-400 text-center">Firecrawl SaaS</th>
                  <th className="py-4 px-4 font-medium text-zinc-400 text-center">Crawl4AI</th>
                  <th className="py-4 px-4 font-medium text-zinc-400 text-center">Jina Reader</th>
                </tr>
              </thead>

              {/* Table Body */}
              <tbody className="divide-y divide-zinc-800/60">
                {filteredDimensions.map((row, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-zinc-800/40 transition-colors"
                  >
                    {/* Dimension Name */}
                    <td className="py-3.5 px-5 text-zinc-200 font-medium font-sans">
                      {row.dimension}
                    </td>

                    {/* DocHarvest Cell (Highlighted) */}
                    <td className="py-3.5 px-4 bg-cyan-950/20 border-x border-cyan-500/20 text-center font-semibold text-cyan-300">
                      <div className="flex items-center justify-center gap-1.5">
                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                        <span>{row.docharvest.value}</span>
                      </div>
                    </td>

                    {/* wget / curl */}
                    <td className="py-3.5 px-4 text-center text-zinc-400">
                      <div className="flex items-center justify-center gap-1.5">
                        {row.wget.pass ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                        )}
                        <span className={row.wget.pass ? "text-zinc-300" : "text-zinc-500"}>
                          {row.wget.value}
                        </span>
                      </div>
                    </td>

                    {/* Firecrawl */}
                    <td className="py-3.5 px-4 text-center text-zinc-400">
                      <div className="flex items-center justify-center gap-1.5">
                        {row.firecrawl.pass ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-rose-500/80 shrink-0" />
                        )}
                        <span className={row.firecrawl.pass ? "text-zinc-300" : "text-zinc-500"}>
                          {row.firecrawl.value}
                        </span>
                      </div>
                    </td>

                    {/* Crawl4AI */}
                    <td className="py-3.5 px-4 text-center text-zinc-400">
                      <div className="flex items-center justify-center gap-1.5">
                        {row.crawl4ai.pass ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                        )}
                        <span className={row.crawl4ai.pass ? "text-zinc-300" : "text-zinc-500"}>
                          {row.crawl4ai.value}
                        </span>
                      </div>
                    </td>

                    {/* Jina */}
                    <td className="py-3.5 px-4 text-center text-zinc-400">
                      <div className="flex items-center justify-center gap-1.5">
                        {row.jina.pass ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                        )}
                        <span className={row.jina.pass ? "text-zinc-300" : "text-zinc-500"}>
                          {row.jina.value}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Matrix Footer */}
          <div className="p-4 bg-zinc-950 border-t border-zinc-800 text-xs text-zinc-400 flex flex-col sm:flex-row items-center justify-between gap-2 font-mono">
            <span>Comparison data verified against v9.0.1 architecture</span>
            <span className="text-cyan-400 font-semibold">100% Free &amp; Open Source (MIT)</span>
          </div>
        </div>
      </div>
    </section>
  )
}
