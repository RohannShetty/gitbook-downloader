import React, { useState } from "react"
import { PERSONA_PATHWAYS, PersonaPathway } from "../data/showcaseData"
import { Cpu, BookOpen, ShieldCheck, Check, Copy, Sparkles, ArrowRight } from "lucide-react"

export const PersonaShowcase: React.FC = () => {
  const [selectedPersona, setSelectedPersona] = useState<PersonaPathway>(PERSONA_PATHWAYS[0])
  const [copied, setCopied] = useState(false)

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getPersonaIcon = (iconName: string) => {
    switch (iconName) {
      case "Cpu":
        return <Cpu className="w-5 h-5 text-cyan-400" />
      case "BookOpen":
        return <BookOpen className="w-5 h-5 text-indigo-400" />
      case "ShieldCheck":
        return <ShieldCheck className="w-5 h-5 text-emerald-400" />
      default:
        return <Cpu className="w-5 h-5 text-cyan-400" />
    }
  }

  return (
    <section id="personas" className="py-24 relative bg-[#0c0c10]">
      {/* Top divider */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>TAILORED DEVELOPER WORKFLOWS</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Built for How You Work
          </h2>
          <p className="text-zinc-400 text-base sm:text-lg">
            Whether you are preparing clean RAG corpora for AI coding agents, compiling offline handbooks for long flights, or auditing API drift in CI/CD pipelines.
          </p>
        </div>

        {/* 3 Persona Cards Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          {PERSONA_PATHWAYS.map((p) => {
            const isSelected = selectedPersona.id === p.id
            return (
              <button
                key={p.id}
                onClick={() => setSelectedPersona(p)}
                className={`p-6 rounded-2xl border text-left transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? "bg-zinc-900 border-cyan-400/60 shadow-xl shadow-cyan-950/20 scale-[1.02]"
                    : "bg-zinc-950/70 border-zinc-800 hover:bg-zinc-900/60 hover:border-zinc-700"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-800">
                      {getPersonaIcon(p.icon)}
                    </div>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                      {p.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{p.title}</h3>
                  <p className="text-xs text-zinc-400 leading-relaxed">{p.tagline}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center text-xs font-medium text-cyan-400">
                  <span>Explore Workflow</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </div>
              </button>
            )
          })}
        </div>

        {/* Active Persona Deep Dive Box */}
        <div className="rounded-2xl bg-zinc-900/90 border border-zinc-800 overflow-hidden shadow-2xl p-6 sm:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left: Challenge & Solution & Metrics */}
            <div className="lg:col-span-7 space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400">
                    {selectedPersona.badge}
                  </span>
                </div>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                  {selectedPersona.title}
                </h3>
              </div>

              {/* Challenge vs Solution */}
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs leading-relaxed text-zinc-300">
                  <span className="font-bold text-rose-400 block mb-1">The Core Challenge:</span>
                  {selectedPersona.challenge}
                </div>

                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs leading-relaxed text-zinc-300">
                  <span className="font-bold text-emerald-400 block mb-1">DocHarvest Solution:</span>
                  {selectedPersona.solution}
                </div>
              </div>

              {/* Key Impact Metrics */}
              <div className="grid grid-cols-3 gap-3 pt-2">
                {selectedPersona.metrics.map((m, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-zinc-950 border border-zinc-800 text-center">
                    <div className="text-lg sm:text-xl font-bold font-mono text-cyan-300">{m.value}</div>
                    <div className="text-[11px] text-zinc-400 mt-0.5">{m.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Code Example Card */}
            <div className="lg:col-span-5 rounded-xl bg-zinc-950 border border-zinc-800 overflow-hidden shadow-xl">
              <div className="p-3 bg-[#111116] border-b border-zinc-800 flex items-center justify-between">
                <span className="text-xs font-mono text-zinc-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>Workflow Execution</span>
                </span>

                <button
                  onClick={() => handleCopy(selectedPersona.codeSnippet)}
                  className="flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 hover:text-white"
                >
                  {copied ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3 text-zinc-400" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>

              <div className="p-4 font-mono text-xs text-zinc-200 overflow-x-auto select-text bg-[#09090c]">
                <pre className="whitespace-pre-wrap leading-relaxed">
                  {selectedPersona.codeSnippet}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
