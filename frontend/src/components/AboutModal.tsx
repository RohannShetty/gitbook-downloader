import React from "react"
import { 
  Sparkles, 
  Heart, 
  ExternalLink, 
  Github, 
  BookOpen, 
  CheckCircle2, 
  X, 
  Cpu, 
  HardDrive, 
  Terminal, 
  Layers,
  FileCode,
  ShieldCheck,
  Globe
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface AboutModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  systemInfo?: {
    name?: string
    version?: string
    engine?: string
    author?: string
    python?: string
    platform?: string
    library_dir?: string
  }
}

export const AboutModal: React.FC<AboutModalProps> = ({
  open,
  onOpenChange,
  systemInfo
}) => {
  if (!open) return null

  const appVersion = systemInfo?.version || "11.0.2"
  const engineVersion = systemInfo?.engine || `DocHarvest Engine v${appVersion} (AST + FastMCP v2 + fpdf2)`
  const authorName = systemInfo?.author || "Rohan Shetty"

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-border/80 bg-card/95 p-6 shadow-2xl shadow-cyan-950/20 backdrop-blur-2xl animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Ambient Top Glow */}
        <div className="absolute -top-24 -left-24 w-60 h-60 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -top-24 -right-24 w-60 h-60 bg-primary/15 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={() => onOpenChange(false)}
          className="absolute right-4 top-4 rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Header Branding */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25">
            <Sparkles className="h-7 w-7 animate-pulse" />
            <div className="absolute inset-0 rounded-2xl bg-cyan-400/20 blur-sm" />
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold tracking-tight text-foreground font-mono">
                DocHarvest
              </h2>
              <Badge variant="outline" className="px-2 py-0.5 text-xs font-mono font-semibold bg-cyan-500/10 text-cyan-400 border-cyan-500/30">
                v{appVersion}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Turn Any Documentation Site into LLM-Ready Markdown, Vector Context &amp; Offline Books
            </p>
          </div>
        </div>

        {/* Specs Matrix */}
        <div className="grid grid-cols-2 gap-2.5 mb-5 text-xs">
          <div className="p-3 rounded-xl border border-border/60 bg-muted/40 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-muted-foreground font-medium">
              <Cpu className="h-3.5 w-3.5 text-cyan-400" />
              <span>Engine Core</span>
            </div>
            <span className="font-mono text-[11px] font-semibold text-foreground truncate">
              {engineVersion}
            </span>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-muted/40 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-muted-foreground font-medium">
              <Terminal className="h-3.5 w-3.5 text-emerald-400" />
              <span>Runtime &amp; GUI</span>
            </div>
            <span className="font-mono text-[11px] font-semibold text-foreground truncate">
              React 18 + WebView2 · Python {systemInfo?.python || "3.12"}
            </span>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-muted/40 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-muted-foreground font-medium">
              <FileCode className="h-3.5 w-3.5 text-purple-400" />
              <span>AI Integration</span>
            </div>
            <span className="font-mono text-[11px] font-semibold text-foreground truncate">
              FastMCP Server · RAG JSONL · llms.txt
            </span>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-muted/40 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-muted-foreground font-medium">
              <ShieldCheck className="h-3.5 w-3.5 text-amber-400" />
              <span>License &amp; Privacy</span>
            </div>
            <span className="font-mono text-[11px] font-semibold text-foreground truncate">
              MIT License · 100% Local &amp; Private
            </span>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="p-3.5 rounded-xl border border-border/60 bg-muted/20 mb-5 space-y-1.5 text-xs text-muted-foreground">
          <div className="flex items-center gap-2 text-foreground font-medium">
            <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
            <span>Universal Scoper &amp; AST Cleaner for GitBook, Mintlify, Docusaurus &amp; SPAs</span>
          </div>
          <div className="flex items-center gap-2 text-foreground font-medium">
            <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
            <span>Deterministic Four-Part Output Contract (Pages, book.md, llms.txt, PDF)</span>
          </div>
          <div className="flex items-center gap-2 text-foreground font-medium">
            <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
            <span>Zero-Crash Domain Locks with Automatic Dead-Process PID Reclamation</span>
          </div>
        </div>

        {/* Made with Love Banner */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-gradient-to-r from-cyan-500/10 via-primary/10 to-purple-500/10 border border-cyan-500/20 mb-5">
          <div className="flex items-center gap-2">
            <Heart className="h-4 w-4 text-rose-500 fill-rose-500 animate-pulse" />
            <span className="text-xs font-semibold text-foreground">
              Made with Love by <span className="text-cyan-400 font-bold">{authorName}</span>
            </span>
          </div>
          <span className="text-[11px] font-mono text-muted-foreground">
            shettyrohan2@gmail.com
          </span>
        </div>

        {/* Action Links */}
        <div className="flex items-center justify-between pt-2 border-t border-border/60">
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/RohannShetty/gitbook-downloader"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors font-medium"
            >
              <Github className="h-3.5 w-3.5" />
              <span>GitHub Repo</span>
              <ExternalLink className="h-3 w-3 opacity-60" />
            </a>

            <a
              href="https://rohannshetty.github.io/gitbook-downloader/"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors font-medium"
            >
              <Globe className="h-3.5 w-3.5" />
              <span>Showcase Site</span>
              <ExternalLink className="h-3 w-3 opacity-60" />
            </a>
          </div>

          <Button 
            size="sm" 
            onClick={() => onOpenChange(false)} 
            className="h-8 px-4 text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm interactive-scale"
          >
            Got it
          </Button>
        </div>
      </div>
    </div>
  )
}
