import React, { useState, useEffect, useRef } from "react"
import { Play, Pause, RotateCcw, Copy, Check, Terminal, Sparkles, FastForward } from "lucide-react"
import { TERMINAL_SCRIPT_STEPS } from "../data/showcaseData"

export const TerminalHero: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [isPlaying, setIsPlaying] = useState(true)
  const [speed, setSpeed] = useState<1 | 2 | 3>(1)
  const [typedCommand, setTypedCommand] = useState("")
  const [copied, setCopied] = useState(false)
  const [activePreset, setActivePreset] = useState<"gitbook" | "mintlify" | "docusaurus">("gitbook")

  const fullCommand = activePreset === "gitbook"
    ? "docharvest capture https://docs.openalgo.in/ --export jsonl,pdf"
    : activePreset === "mintlify"
    ? "docharvest capture https://mintlify.com/docs --export jsonl"
    : "docharvest capture https://docusaurus.io/docs --export pdf"

  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Typing effect for the command line
  useEffect(() => {
    let charIndex = 0
    setTypedCommand("")
    setCurrentStep(1)

    const baseDelay = 35 / speed

    const typingInterval = setInterval(() => {
      if (charIndex < fullCommand.length) {
        setTypedCommand(fullCommand.slice(0, charIndex + 1))
        charIndex++
      } else {
        clearInterval(typingInterval)
        // Move to execution steps
        if (isPlaying) {
          progressSteps()
        }
      }
    }, baseDelay)

    return () => clearInterval(typingInterval)
  }, [activePreset, speed])

  const progressSteps = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)

    const stepDelay = 1200 / speed

    let step = 1
    intervalRef.current = setInterval(() => {
      step++
      if (step <= TERMINAL_SCRIPT_STEPS.length) {
        setCurrentStep(step)
      } else {
        if (intervalRef.current) clearInterval(intervalRef.current)
      }
    }, stepDelay)
  }

  const handleReplay = () => {
    setIsPlaying(true)
    setTypedCommand("")
    setCurrentStep(1)
    let charIndex = 0
    const typingInterval = setInterval(() => {
      if (charIndex < fullCommand.length) {
        setTypedCommand(fullCommand.slice(0, charIndex + 1))
        charIndex++
      } else {
        clearInterval(typingInterval)
        progressSteps()
      }
    }, 35 / speed)
  }

  const togglePlay = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying) {
      if (currentStep >= TERMINAL_SCRIPT_STEPS.length) {
        handleReplay()
      } else {
        progressSteps()
      }
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }

  const handleCopyCommand = () => {
    navigator.clipboard.writeText(fullCommand)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="w-full max-w-4xl mx-auto rounded-2xl bg-[#101014] border border-zinc-800/90 shadow-2xl shadow-cyan-950/20 overflow-hidden text-left relative group">
      {/* Glow Effect behind terminal */}
      <div className="absolute -top-12 -right-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-12 -left-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#15151b] border-b border-zinc-800/80">
        {/* macOS Window Controls */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ff5f56] border border-[#e0443e]/50" />
          <div className="w-3 h-3 rounded-full bg-[#ffbd2e] border border-[#dea123]/50" />
          <div className="w-3 h-3 rounded-full bg-[#27c93f] border border-[#1aab29]/50" />
          <span className="ml-2 text-xs font-mono text-zinc-400 hidden sm:inline-block">
            docharvest — zsh — 80x24
          </span>
        </div>

        {/* Live Preset Switcher */}
        <div className="flex items-center gap-1.5 bg-zinc-900/90 border border-zinc-800 rounded-lg p-0.5">
          <button
            onClick={() => setActivePreset("gitbook")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-all ${
              activePreset === "gitbook"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            GitBook
          </button>
          <button
            onClick={() => setActivePreset("mintlify")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-all ${
              activePreset === "mintlify"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Mintlify
          </button>
          <button
            onClick={() => setActivePreset("docusaurus")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-all ${
              activePreset === "docusaurus"
                ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Docusaurus
          </button>
        </div>

        {/* Right Controls: Playback, Speed, Copy */}
        <div className="flex items-center gap-2">
          {/* Speed Toggle */}
          <button
            onClick={() => setSpeed(speed === 1 ? 2 : speed === 2 ? 3 : 1)}
            className="flex items-center gap-1 px-2 py-1 rounded bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 hover:border-zinc-700 transition-colors"
            title="Toggle playback speed"
          >
            <FastForward className="w-3 h-3 text-cyan-400" />
            <span>{speed}x</span>
          </button>

          {/* Replay */}
          <button
            onClick={handleReplay}
            className="p-1.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700 transition-colors"
            title="Replay sequence"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Copy Command */}
          <button
            onClick={handleCopyCommand}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 hover:text-white hover:border-zinc-700 transition-colors"
            title="Copy full CLI command"
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
      </div>

      {/* Terminal Screen Canvas */}
      <div className="p-5 font-mono text-xs sm:text-sm text-zinc-200 leading-relaxed min-h-[340px] bg-[#0c0c10] select-text">
        {/* Command Line Prompt */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-cyan-400 font-bold">❯</span>
          <span className="text-zinc-100 font-semibold">{typedCommand}</span>
          {typedCommand.length < fullCommand.length && (
            <span className="inline-block w-2 h-4 bg-cyan-400 animate-pulse ml-0.5" />
          )}
        </div>

        {/* Dynamic Execution Output */}
        {typedCommand.length >= fullCommand.length && (
          <div className="space-y-3 animate-in fade-in duration-300">
            {/* Step 1: Heuristic inspection */}
            {currentStep >= 1 && (
              <div className="space-y-1 text-zinc-400 border-l-2 border-cyan-500/40 pl-3">
                <div className="text-zinc-300">
                  <span className="text-cyan-400">⚡</span> Probing platform heuristics and direct .md endpoints...
                </div>
                <div className="text-cyan-300 flex items-center gap-1.5">
                  <span className="text-emerald-400">✓</span>
                  <span>
                    Detected provider:{" "}
                    <strong className="text-white font-semibold capitalize">{activePreset}</strong>
                    {" "}(Priority match: 100/100)
                  </span>
                </div>
                <div className="text-zinc-400">
                  <span className="text-emerald-400">✓</span> Auto-scoped doc subpath to documentation root.
                </div>
              </div>
            )}

            {/* Step 2: Download progress */}
            {currentStep >= 2 && (
              <div className="space-y-1.5 pl-3 border-l-2 border-indigo-500/40 text-zinc-300">
                <div className="flex items-center gap-2">
                  <span className="text-indigo-400">📥</span>
                  <span>Streaming clean Markdown (5 parallel worker threads)...</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-48 sm:w-64 h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-400 to-indigo-500 rounded-full w-full animate-in slide-in-from-left duration-700" />
                  </div>
                  <span className="text-xs text-cyan-300 font-semibold">673/673 pages (100%)</span>
                </div>
              </div>
            )}

            {/* Step 3: Four-Part Output Contract tree */}
            {currentStep >= 3 && (
              <div className="space-y-1 pl-3 border-l-2 border-emerald-500/40 text-zinc-300">
                <div className="text-zinc-100 font-medium flex items-center gap-1.5">
                  <span className="text-emerald-400">📦</span> Generated Four-Part Output Contract:
                </div>
                <div className="font-mono text-xs pl-2 space-y-0.5">
                  <div className="text-zinc-300">
                    ├── <span className="text-cyan-300 font-semibold">docs/pages/</span> (673 clean .md files + SHA-256 YAML frontmatter)
                  </div>
                  <div className="text-zinc-300">
                    ├── <span className="text-indigo-300 font-semibold">book.md</span> (unified handbook with natural reading order &amp; TOC)
                  </div>
                  <div className="text-zinc-300">
                    ├── <span className="text-emerald-300 font-semibold">llms.txt</span> (standardized AI discovery manifest)
                  </div>
                  <div className="text-zinc-300">
                    ├── <span className="text-amber-300 font-semibold">exports/rag_dataset.jsonl</span> (vector chunks + metadata wrappers)
                  </div>
                  <div className="text-zinc-300">
                    └── <span className="text-rose-300 font-semibold">exports/handbook.pdf</span> (pure-Python printable PDF via fpdf2)
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: SQLite index completion */}
            {currentStep >= 4 && (
              <div className="mt-3 pt-2 border-t border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div className="text-emerald-400 font-semibold flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>Indexed to local SQLite FTS5 database in 18.2s (BM25 porter unicode61)!</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-mono">
                  Ready for Cursor &amp; Claude
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Terminal Footer Status Bar */}
      <div className="px-4 py-2 bg-[#0e0e12] border-t border-zinc-800/80 flex items-center justify-between text-[11px] font-mono text-zinc-500">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            READY
          </span>
          <span>Engine: Python 3.10+ / AST Splitter</span>
        </div>
        <div className="hidden sm:flex items-center gap-4">
          <span>Concurrency: 5 threads</span>
          <span>Mode: Air-gapped / Local</span>
        </div>
      </div>
    </div>
  )
}
