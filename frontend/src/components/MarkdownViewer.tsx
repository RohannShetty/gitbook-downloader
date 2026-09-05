import React, { useEffect, useRef, useState, useMemo } from "react"
import {
  Copy,
  Check,
  Download,
  FileText,
  Search,
  List,
  ChevronRight,
  Sparkles,
  ExternalLink,
  Code,
  BookOpen,
  Maximize2,
  Minimize2
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import mermaid from "mermaid"

interface MarkdownViewerProps {
  content: string
  title?: string
  domain?: string
  theme?: "dark" | "light"
  onClose?: () => void
  onExportPdf?: () => void
}

interface TocItem {
  id: string
  text: string
  level: number
}

// Theme-aware, re-runnable Mermaid initialization. The dark palette is pinned
// (must not regress); the light palette uses a near-white background with dark
// strokes/text so diagrams stay readable on light glass cards.
let activeMermaidTheme: "dark" | "light" | null = null

export function initMermaid(theme: "dark" | "light"): void {
  if (activeMermaidTheme === theme) return
  if (theme === "dark") {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        darkMode: true,
        background: "#090d16",
        primaryColor: "#06b6d4",
        primaryTextColor: "#f8fafc",
        lineColor: "#38bdf8",
        secondaryColor: "#10b981",
        tertiaryColor: "#6366f1"
      },
      securityLevel: "loose"
    })
  } else {
    mermaid.initialize({
      startOnLoad: false,
      theme: "default",
      themeVariables: {
        darkMode: false,
        background: "#ffffff",
        primaryColor: "#e0f2fe",
        primaryTextColor: "#0f172a",
        primaryBorderColor: "#0369a1",
        lineColor: "#475569",
        secondaryColor: "#d1fae5",
        tertiaryColor: "#e0e7ff",
        textColor: "#0f172a",
        edgeLabelBackground: "#ffffff"
      },
      securityLevel: "loose"
    })
  }
  activeMermaidTheme = theme
}

// Initial configuration (the app boots in dark mode; see index.html).
initMermaid("dark")

export const MarkdownViewer: React.FC<MarkdownViewerProps> = ({
  content,
  title,
  domain,
  theme,
  onClose,
  onExportPdf
}) => {
  const [copied, setCopied] = useState<boolean>(false)
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [activeHeadingId, setActiveHeadingId] = useState<string>("")
  const [showToc, setShowToc] = useState<boolean>(true)
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false)

  const contentRef = useRef<HTMLDivElement>(null)

  // Effective theme: explicit prop wins; otherwise read the class App.tsx
  // toggles on <html>. Re-rendering diagrams is keyed on this value.
  const resolvedTheme: "dark" | "light" =
    theme ?? (document.documentElement.classList.contains("dark") ? "dark" : "light")

  // Metrics computation
  const stats = useMemo(() => {
    const words = content.trim().split(/\s+/).filter(Boolean).length
    const chars = content.length
    const readingTimeMin = Math.max(1, Math.ceil(words / 200))
    const codeBlocks = (content.match(/```/g) || []).length / 2
    return { words, chars, readingTimeMin, codeBlocks: Math.floor(codeBlocks) }
  }, [content])

  // Extract Table of Contents
  const toc: TocItem[] = useMemo(() => {
    const items: TocItem[] = []
    const lines = content.split("\n")
    lines.forEach((line, idx) => {
      const match = line.match(/^(#{1,4})\s+(.+)$/)
      if (match) {
        const level = match[1].length
        const rawText = match[2].trim()
        const text = rawText.replace(/[*_`#]/g, "")
        const id = `heading-${idx}-${text.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`
        items.push({ id, text, level })
      }
    })
    return items
  }, [content])

  // Render Mermaid diagrams whenever the content or the theme changes. Every
  // block is reset to its raw source first, so a theme switch always regenerates
  // the SVGs with the active palette and never leaves stale dark SVGs behind.
  useEffect(() => {
    if (!contentRef.current) return

    initMermaid(resolvedTheme)

    const mermaidBlocks = contentRef.current.querySelectorAll("pre.mermaid-block")
    mermaidBlocks.forEach((el) => {
      const code = el.getAttribute("data-code") || ""
      el.classList.remove("mermaid-rendered")
      if (code) el.textContent = code
    })

    let cancelled = false
    mermaidBlocks.forEach((el, index) => {
      const code = el.getAttribute("data-code") || el.textContent || ""
      if (!code) return
      void (async () => {
        try {
          const id = `mermaid-svg-${Date.now()}-${index}`
          const { svg } = await mermaid.render(id, code)
          if (cancelled) return
          el.innerHTML = svg
          el.classList.add("mermaid-rendered")
        } catch (err) {
          console.warn("Mermaid rendering error:", err)
        }
      })()
    })

    return () => {
      cancelled = true
    }
  }, [content, resolvedTheme])

  // Scrollspy observer for active heading
  useEffect(() => {
    const handleScroll = () => {
      if (!contentRef.current) return
      const headings = contentRef.current.querySelectorAll("[data-heading-id]")
      let currentId = ""
      const scrollPos = contentRef.current.scrollTop + 100

      headings.forEach((h) => {
        const top = (h as HTMLElement).offsetTop
        if (top <= scrollPos) {
          currentId = h.getAttribute("data-heading-id") || ""
        }
      })
      if (currentId) setActiveHeadingId(currentId)
    }

    const container = contentRef.current
    if (container) {
      container.addEventListener("scroll", handleScroll, { passive: true })
      return () => container.removeEventListener("scroll", handleScroll)
    }
  }, [])

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    toast.success("Markdown copied to clipboard!")
    setTimeout(() => setCopied(false), 2000)
  }

  const handleScrollToHeading = (id: string) => {
    if (!contentRef.current) return
    const el = contentRef.current.querySelector(`[data-heading-id="${id}"]`)
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" })
      setActiveHeadingId(id)
    }
  }

  // Simple, robust HTML parser for Markdown content
  const renderFormattedContent = () => {
    const lines = content.split("\n")
    const elements: React.ReactNode[] = []
    let inCodeBlock = false
    let codeLanguage = ""
    let codeBuffer: string[] = []

    lines.forEach((line, index) => {
      // Code block start/end
      if (line.startsWith("```")) {
        if (!inCodeBlock) {
          inCodeBlock = true
          codeLanguage = line.slice(3).trim()
          codeBuffer = []
          return
        } else {
          inCodeBlock = false
          const codeText = codeBuffer.join("\n")
          const isMermaid = codeLanguage.toLowerCase() === "mermaid"

          if (isMermaid) {
            elements.push(
              <div key={`mermaid-${index}-${resolvedTheme}`} className="my-6 rounded-xl border border-cyan-500/20 bg-background/80 p-4 shadow-sm">
                <div className="flex items-center justify-between border-b border-border/50 pb-2 mb-3 text-xs text-muted-foreground font-mono">
                  <span className="flex items-center gap-1.5 text-cyan-700 dark:text-cyan-400">
                    <Sparkles className="h-3.5 w-3.5" /> Mermaid Architecture Diagram
                  </span>
                </div>
                <pre
                  className="mermaid-block overflow-x-auto text-center font-sans"
                  data-code={codeText}
                >
                  {codeText}
                </pre>
              </div>
            )
          } else {
            elements.push(
              <div key={`code-${index}`} className="group relative my-5 rounded-xl border border-border/60 bg-[#090d16] text-slate-100 shadow-md">
                <div className="flex items-center justify-between border-b border-white/10 px-4 py-2 text-xs font-mono text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <Code className="h-3.5 w-3.5 text-cyan-400" />
                    {codeLanguage || "text"}
                  </span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(codeText)
                      toast.success("Code snippet copied!")
                    }}
                    className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    <Copy className="h-3 w-3" /> Copy
                  </button>
                </div>
                <pre className="overflow-x-auto p-4 font-mono text-xs leading-relaxed">
                  <code>{codeText}</code>
                </pre>
              </div>
            )
          }
          return
        }
      }

      if (inCodeBlock) {
        codeBuffer.push(line)
        return
      }

      // Headings
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/)
      if (headingMatch) {
        const level = headingMatch[1].length
        const rawText = headingMatch[2].trim()
        const cleanText = rawText.replace(/[*_`#]/g, "")
        const headingId = `heading-${index}-${cleanText.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`

        const isMatch = searchQuery && cleanText.toLowerCase().includes(searchQuery.toLowerCase())

        if (level === 1) {
          elements.push(
            <h1
              key={`h1-${index}`}
              data-heading-id={headingId}
              className={`mt-8 mb-4 text-2xl font-bold tracking-tight text-foreground border-b border-border/50 pb-2 ${
                isMatch ? "bg-amber-500/20 px-2 rounded" : ""
              }`}
            >
              {cleanText}
            </h1>
          )
        } else if (level === 2) {
          elements.push(
            <h2
              key={`h2-${index}`}
              data-heading-id={headingId}
              className={`mt-6 mb-3 text-xl font-semibold tracking-tight text-foreground ${
                isMatch ? "bg-amber-500/20 px-2 rounded" : ""
              }`}
            >
              {cleanText}
            </h2>
          )
        } else if (level === 3) {
          elements.push(
            <h3
              key={`h3-${index}`}
              data-heading-id={headingId}
              className={`mt-4 mb-2 text-base font-semibold text-foreground/90 ${
                isMatch ? "bg-amber-500/20 px-2 rounded" : ""
              }`}
            >
              {cleanText}
            </h3>
          )
        } else {
          elements.push(
            <h4
              key={`h4-${index}`}
              data-heading-id={headingId}
              className={`mt-3 mb-1 text-sm font-semibold text-foreground/80 ${
                isMatch ? "bg-amber-500/20 px-2 rounded" : ""
              }`}
            >
              {cleanText}
            </h4>
          )
        }
        return
      }

      // Blockquotes
      if (line.startsWith("> ")) {
        elements.push(
          <blockquote
            key={`bq-${index}`}
            className="my-3 border-l border-border pl-4 py-1 text-xs italic text-muted-foreground"
          >
            {line.slice(2)}
          </blockquote>
        )
        return
      }

      // Bullet lists
      if (line.match(/^[\*\-]\s+/)) {
        elements.push(
          <li key={`li-${index}`} className="ml-5 list-disc text-xs leading-relaxed text-foreground/90 my-1">
            {line.replace(/^[\*\-]\s+/, "")}
          </li>
        )
        return
      }

      // Numbered lists
      if (line.match(/^\d+\.\s+/)) {
        elements.push(
          <li key={`nli-${index}`} className="ml-5 list-decimal text-xs leading-relaxed text-foreground/90 my-1">
            {line.replace(/^\d+\.\s+/, "")}
          </li>
        )
        return
      }

      // Horizontal rules
      if (line.match(/^(\-{3,}|\*{3,}|_{3,})$/)) {
        elements.push(<hr key={`hr-${index}`} className="my-6 border-border/60" />)
        return
      }

      // Empty lines
      if (!line.trim()) {
        elements.push(<div key={`sp-${index}`} className="h-2" />)
        return
      }

      // Standard paragraphs
      elements.push(
        <p key={`p-${index}`} className="my-2 text-xs leading-relaxed text-foreground/90">
          {line}
        </p>
      )
    })

    return elements
  }

  return (
    <div className={`flex flex-col h-full bg-background border border-border/80 rounded-xl overflow-hidden shadow-2xl ${
      isFullscreen ? "fixed inset-2 z-50 rounded-2xl" : "relative"
    }`}>
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-border bg-card/80 px-4 py-3 backdrop-blur-md">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
            <BookOpen className="h-4 w-4" />
          </div>
          <div className="flex flex-col overflow-hidden">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm truncate text-foreground font-mono">
                {title || domain || "Documentation Viewer"}
              </span>
              {domain && (
                <Badge variant="outline" className="text-[10px] font-mono border-primary/30 text-primary">
                  {domain}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
              <span>{stats.words.toLocaleString()} words</span>
              <span>•</span>
              <span>~{stats.readingTimeMin} min read</span>
              <span>•</span>
              <span>{stats.codeBlocks} code snippets</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Quick Search */}
          <div className="relative w-48 hidden sm:block">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-8 text-xs bg-background/50 border-border/60"
            />
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowToc(!showToc)}
            className={`h-8 gap-1.5 text-xs ${showToc ? "bg-accent text-accent-foreground" : ""}`}
            title="Toggle Table of Contents"
          >
            <List className="h-3.5 w-3.5" />
            <span className="hidden md:inline">TOC</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyMarkdown}
            className="h-8 gap-1.5 text-xs"
            title="Copy Raw Markdown"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span className="hidden md:inline">{copied ? "Copied" : "Copy MD"}</span>
          </Button>

          {onExportPdf && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportPdf}
              className="h-8 gap-1.5 text-xs border-cyan-500/30 text-cyan-700 hover:bg-cyan-500/10 dark:text-cyan-400"
              title="Export as Pure-Python PDF Handbook"
            >
              <Download className="h-3.5 w-3.5" />
              <span className="hidden md:inline">PDF</span>
            </Button>
          )}

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>

          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 text-xs text-muted-foreground hover:text-foreground"
            >
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Split Workspace: TOC Sidebar + Content Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Dynamic Table of Contents Sidebar */}
        {showToc && toc.length > 0 && (
          <aside className="w-64 border-r border-border bg-card/40 backdrop-blur-sm p-4 overflow-y-auto hidden sm:block select-none">
            <div className="flex items-center justify-between pb-3 mb-2 border-b border-border/50 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              <span>Table of Contents</span>
              <Badge variant="secondary" className="text-[10px] h-4 px-1.5">
                {toc.length}
              </Badge>
            </div>
            <nav className="space-y-1">
              {toc.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleScrollToHeading(item.id)}
                  className={`group flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-xs transition-colors ${
                    activeHeadingId === item.id
                      ? "bg-primary/10 text-primary font-medium border border-primary/20"
                      : "text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                  } ${item.level === 2 ? "pl-4 text-[11px]" : item.level >= 3 ? "pl-6 text-[10px]" : "font-medium"}`}
                >
                  <ChevronRight className={`h-3 w-3 shrink-0 opacity-0 group-hover:opacity-100 ${
                    activeHeadingId === item.id ? "opacity-100 text-primary" : ""
                  }`} />
                  <span className="truncate">{item.text}</span>
                </button>
              ))}
            </nav>
          </aside>
        )}

        {/* Main Formatted Markdown Body */}
        <div
          ref={contentRef}
          className="flex-1 overflow-y-auto p-6 md:p-8 font-sans antialiased text-foreground selection:bg-cyan-500/20 selection:text-cyan-700 dark:selection:text-cyan-300"
        >
          <div className="max-w-4xl mx-auto">
            {renderFormattedContent()}
          </div>
        </div>
      </div>
    </div>
  )
}
