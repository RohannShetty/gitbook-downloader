import React, { useState, useEffect } from "react"
import {
  Sparkles,
  Download,
  Library,
  FileUp,
  Cpu,
  Command,
  ChevronRight,
  ChevronLeft,
  X,
  CheckCircle2,
  Layers,
  Search
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface OnboardingTourProps {
  open: boolean
  onClose: () => void
}

interface TourStep {
  title: string
  subtitle: string
  description: string
  icon: React.ElementType
  badge: string
  tips: string[]
}

const TOUR_STEPS: TourStep[] = [
  {
    title: "Welcome to DocHarvest v11",
    subtitle: "Turn Any Documentation Site into LLM-Ready Markdown & Vector Context",
    description: "DocHarvest is a local-first documentation harvester, AI context compiler, and FastMCP server. It cleans up to 89% of token-wasting navigation boilerplate and outputs structured knowledge corpora.",
    icon: Sparkles,
    badge: "v11.0.3 Architecture",
    tips: [
      "100% local, zero telemetry, zero cloud fees",
      "8 dedicated documentation platform providers",
      "Process-safe atomic storage and version diffing"
    ]
  },
  {
    title: "⚡ Capture Studio & SPA Rendering",
    subtitle: "Automated Platform Sniffing with Headless Playwright Fallback",
    description: "Paste any documentation URL. DocHarvest auto-detects GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe, and ReadTheDocs. For client-rendered SPAs, toggle Headless Rendering to execute JS before capture.",
    icon: Download,
    badge: "Smart Discovery",
    tips: [
      "Auto-probes raw .md endpoints directly for zero HTML noise",
      "Path scoping lets you restrict crawls to specific subpaths (e.g. /api/)",
      "Loud diagnostics warn when a target is an empty JS shell"
    ]
  },
  {
    title: "📚 Document Library & Instant Search",
    subtitle: "Manage, Rename & Browse Harvested Docsets",
    description: "Your local knowledge vault stores every harvested documentation portal. Search across hundreds of pages in milliseconds via SQLite FTS5 (BM25 stemming), rename projects, or view formatted docs in the in-app reader.",
    icon: Library,
    badge: "Local Knowledge Vault",
    tips: [
      "Rename project display labels without breaking file paths",
      "Open raw Markdown folders in File Explorer / Finder with 1 click",
      "Compare snapshots over time to inspect library changes"
    ]
  },
  {
    title: "📦 AI Export Studio & Pure-Python PDF",
    subtitle: "Vector Ingestion (JSONL) & Printable Books (fpdf2)",
    description: "Transform raw documentation into downstream AI artifacts: RAG JSONL chunks for LangChain/LlamaIndex, AST header-split markdown, and publication-grade PDF handbooks generated using pure-Python fpdf2.",
    icon: FileUp,
    badge: "RAG & PDF Studio",
    tips: [
      "Embeddings-ready tokenized chunks with clean frontmatter",
      "Printable offline PDF handbooks with table of contents",
      "Standardized llms.txt generated at output root"
    ]
  },
  {
    title: "🔌 Native FastMCP v2 Server",
    subtitle: "Expose 10 Tools, Prompts & Resources to AI IDEs",
    description: "Seamlessly connect Cursor, Claude Code, Windsurf, VS Code, Zed, and JetBrains. DocHarvest exposes tools like download_docs, search_docs, get_doc, and query_doc_graph over stdio with zero configuration.",
    icon: Cpu,
    badge: "MCP v2 Protocol",
    tips: [
      "Run 'docharvest mcp' to connect any AI IDE",
      "Compatible with both mcp<2 and mcp>=2 runtimes",
      "Semantic graph querying prevents context window overflow"
    ]
  },
  {
    title: "⌨️ Command Palette & Shortcuts",
    subtitle: "Speed Up Workflows with Keyboard Navigation",
    description: "Press Ctrl+K (or Cmd+K on Mac) anywhere in the application to jump between studios, search downloaded docs, start crawls, and switch light/dark themes instantly.",
    icon: Command,
    badge: "Pro Productivity",
    tips: [
      "Ctrl+K: Open universal command palette",
      "Light/Dark Mode toggle in sidebar footer",
      "View in-app documentation anytime from the sidebar"
    ]
  }
]

export const OnboardingTour: React.FC<OnboardingTourProps> = ({ open, onClose }) => {
  const [currentStep, setCurrentStep] = useState<number>(0)

  useEffect(() => {
    if (open) {
      setCurrentStep(0)
    }
  }, [open])

  if (!open) return null

  const step = TOUR_STEPS[currentStep]
  const Icon = step.icon
  const isLast = currentStep === TOUR_STEPS.length - 1

  const handleNext = () => {
    if (isLast) {
      localStorage.setItem("docharvest_tour_completed", "true")
      onClose()
    } else {
      setCurrentStep((prev) => prev + 1)
    }
  }

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(0, prev - 1))
  }

  const handleSkip = () => {
    localStorage.setItem("docharvest_tour_completed", "true")
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 animate-in fade-in duration-200 select-none">
      <div className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-cyan-500/30 bg-card/95 shadow-2xl backdrop-blur-2xl">
        {/* Glow accent */}
        <div className="absolute -top-24 -left-24 h-48 w-48 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute -bottom-24 -right-24 h-48 w-48 rounded-full bg-blue-600/20 blur-3xl" />

        {/* Header */}
        <div className="relative flex items-center justify-between border-b border-border/80 px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              DocHarvest Interactive Tour
            </span>
          </div>
          <button
            onClick={handleSkip}
            className="rounded-lg p-1 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="relative p-6 sm:p-8 space-y-6">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400 shadow-md">
              <Icon className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold tracking-tight text-foreground font-mono">
                  {step.title}
                </h3>
                <Badge variant="outline" className="text-[10px] border-cyan-500/30 text-cyan-400 font-mono">
                  {step.badge}
                </Badge>
              </div>
              <p className="text-xs font-medium text-muted-foreground">
                {step.subtitle}
              </p>
            </div>
          </div>

          <p className="text-xs leading-relaxed text-foreground/85 bg-background/50 p-3.5 rounded-xl border border-border/60">
            {step.description}
          </p>

          {/* Key Tips */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider font-mono">
              Key Highlights:
            </span>
            <div className="space-y-1.5">
              {step.tips.map((tip, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-foreground/90">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Progress Indicators */}
          <div className="flex items-center justify-center gap-1.5 pt-2">
            {TOUR_STEPS.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentStep(idx)}
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  idx === currentStep
                    ? "w-8 bg-cyan-400"
                    : idx < currentStep
                    ? "w-2.5 bg-primary/40"
                    : "w-2.5 bg-muted"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="relative flex items-center justify-between border-t border-border/80 bg-background/60 px-6 py-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSkip}
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Skip Tour
          </Button>

          <div className="flex items-center gap-2">
            {currentStep > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrev}
                className="h-8 gap-1 text-xs"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
                Previous
              </Button>
            )}

            <Button
              size="sm"
              onClick={handleNext}
              className="h-8 gap-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm"
            >
              {isLast ? "Get Started" : "Next"}
              {!isLast && <ChevronRight className="h-3.5 w-3.5" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
