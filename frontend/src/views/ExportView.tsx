import React, { useState } from "react"
import { 
  FileUp, 
  FileText, 
  FileSpreadsheet, 
  BookOpen, 
  Sparkles, 
  FolderOpen, 
  CheckCircle2, 
  ArrowRight,
  Database,
  ExternalLink,
  Folder,
  Layers,
  FileCode,
  Check
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface ExportViewProps {
  library: any[]
  selectedDomain?: string
}

export const ExportView: React.FC<ExportViewProps> = ({ library, selectedDomain: defaultDomain }) => {
  const [domain, setDomain] = useState<string>(defaultDomain || library[0]?.domain || "")
  const [format, setFormat] = useState<"md" | "pdf" | "jsonl">("jsonl")
  const [customPath, setCustomPath] = useState<string>("")
  const [exporting, setExporting] = useState<boolean>(false)
  const [lastExport, setLastExport] = useState<any>(null)

  const handleExport = async () => {
    if (!domain) {
      toast.error("Please select a documentation source from your library")
      return
    }

    setExporting(true)
    setLastExport(null)
    try {
      const res = await pyApi.exportDoc(domain, format, customPath.trim() || undefined)
      if (res.success) {
        setLastExport(res)
        toast.success(`Successfully generated ${format.toUpperCase()} export for ${domain}`)
      } else {
        toast.error(`Export failed: ${res.error}`)
      }
    } catch (err: any) {
      toast.error(`Export error: ${err.message}`)
    } finally {
      setExporting(false)
    }
  }

  const exportFormats = [
    {
      id: "jsonl" as const,
      title: "JSONL (AI Vector & RAG Dataset)",
      icon: Database,
      desc: "Page-by-page JSON lines with chunking metadata, source URLs, and document hierarchies. Ideal for LangChain, LlamaIndex, OpenAI embeddings, and ChromaDB.",
      badge: "RAG Recommended",
      badgeColor: "border-primary/40 text-primary bg-primary/10",
    },
    {
      id: "pdf" as const,
      title: "PDF Printable Handbook",
      icon: FileSpreadsheet,
      desc: "Compiled single-file printable documentation handbook with structured headings, code syntax highlighting, and clean typography.",
      badge: "Handbook / Print",
      badgeColor: "border-emerald-500/40 text-emerald-400 bg-emerald-500/10",
    },
    {
      id: "md" as const,
      title: "Single Markdown (book.md)",
      icon: FileText,
      desc: "Concatenated Markdown handbook with relative internal link rewriting, preserved code blocks, and structured table of contents.",
      badge: "Unified Markdown",
      badgeColor: "border-purple-500/40 text-purple-400 bg-purple-500/10",
    },
  ]

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6 animate-in fade-in-50 duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <FileUp className="h-6 w-6 text-primary" />
            <span>Export Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs border border-border bg-muted/60">
            RAG Pipeline & Handbooks
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Transform your captured documentation library into RAG vector datasets (JSONL), PDFs, or unified Markdown books.
        </p>
      </div>

      {/* Domain Selector */}
      <Card className="glass-card shadow-sm">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <span className="flex h-5 w-5 rounded-full bg-primary/10 text-primary items-center justify-center text-xs font-bold font-mono">1</span>
            <span>Select Documentation Source</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Choose which site from your library you wish to export.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-5 pt-0">
          {library.length === 0 ? (
            <div className="text-xs text-muted-foreground italic py-3 bg-muted/20 p-3 rounded-lg border border-dashed border-border/80 text-center">
              No documentation libraries found. Capture a documentation site first in the Capture Studio.
            </div>
          ) : (
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-background border border-border text-foreground rounded-lg p-2.5 text-xs focus:ring-2 focus:ring-primary/40 outline-none font-mono"
            >
              {library.map((item) => (
                <option key={item.domain} value={item.domain}>
                  {item.domain} — {item.title || item.domain} ({item.pages || item.pages_count || 0} pages)
                </option>
              ))}
            </select>
          )}
        </CardContent>
      </Card>

      {/* Format Chooser */}
      <Card className="glass-card shadow-sm">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <span className="flex h-5 w-5 rounded-full bg-primary/10 text-primary items-center justify-center text-xs font-bold font-mono">2</span>
            <span>Choose Output Format</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-5 pt-0 grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {exportFormats.map((f) => {
            const Icon = f.icon
            const isSelected = format === f.id
            return (
              <div
                key={f.id}
                onClick={() => setFormat(f.id)}
                className={`cursor-pointer rounded-xl border p-4.5 transition-all flex flex-col justify-between gap-3 interactive-scale ${
                  isSelected
                    ? "border-primary bg-primary/10 shadow-sm shadow-primary/15"
                    : "border-border/60 bg-background/50 hover:border-primary/40"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2.5">
                    <div className={`p-2.5 rounded-lg ${isSelected ? "bg-primary text-primary-foreground" : "bg-muted/60 text-muted-foreground"}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <Badge variant="outline" className={`text-[10px] font-mono ${f.badgeColor}`}>
                      {f.badge}
                    </Badge>
                  </div>
                  <h4 className="font-semibold text-xs text-foreground mb-1.5">{f.title}</h4>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4.5 rounded-xl border border-border/70 bg-card/60 backdrop-blur-md shadow-sm">
        <div className="text-xs text-muted-foreground">
          Default output directory: <span className="font-mono text-foreground font-semibold">exports/</span>
        </div>
        <Button
          onClick={handleExport}
          disabled={exporting || !domain}
          className="h-11 px-7 font-semibold bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20 interactive-scale"
        >
          {exporting ? (
            <span>Generating Export...</span>
          ) : (
            <>
              <span>Generate {format.toUpperCase()}</span>
              <ArrowRight className="h-4 w-4 ml-2" />
            </>
          )}
        </Button>
      </div>

      {/* Output Feedback */}
      {lastExport && (
        <Card className="border-emerald-500/40 bg-emerald-500/10 backdrop-blur-md shadow-sm p-4.5 animate-in fade-in-50 duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="h-10 w-10 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center shrink-0 border border-emerald-500/30">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div className="overflow-hidden">
                <h4 className="text-xs font-semibold text-foreground">Export Generated Successfully</h4>
                <p className="text-[11px] text-muted-foreground font-mono truncate max-w-lg mt-0.5" title={lastExport.path}>
                  {lastExport.path}
                </p>
              </div>
            </div>
            {lastExport.path && (
              <div className="flex items-center gap-2 shrink-0">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    pyApi.openFile(lastExport.path)
                    toast.info("Opening document...")
                  }}
                  className="text-xs h-8 px-3 border-border bg-background/80 interactive-scale"
                >
                  <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                  Open File
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    pyApi.openFolder(lastExport.path)
                    toast.info("Opening folder in Explorer...")
                  }}
                  className="text-xs h-8 px-3 border-border bg-background/80 interactive-scale"
                >
                  <FolderOpen className="h-3.5 w-3.5 mr-1.5" />
                  Show in Folder
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
