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
  ExternalLink
} from "lucide-react"
import { Button } from "@/components/ui/button"
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
      const res = await pyApi.exportDoc(domain, format)
      if (res.success) {
        setLastExport(res)
        toast.success(`Exported ${domain} as ${format.toUpperCase()}`)
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
      title: "JSONL (RAG / AI Vector Dataset)",
      icon: Database,
      desc: "Page-by-page JSON lines with chunking metadata, source URLs, and titles. Ideal for LangChain, LlamaIndex, OpenAI embeddings, and ChromaDB.",
      badge: "AI Ready",
    },
    {
      id: "pdf" as const,
      title: "PDF / Standalone HTML Document",
      icon: FileSpreadsheet,
      desc: "Compiled single-file printable documentation handbook with structured headings, code syntax, and clean reading typography.",
      badge: "Print / Share",
    },
    {
      id: "md" as const,
      title: "Single Markdown (book.md)",
      icon: FileText,
      desc: "Concatenated Markdown handbook with relative internal link preservation, code blocks, and full TOC table.",
      badge: "Universal MD",
    },
  ]

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
            <FileUp className="h-6 w-6 text-primary" />
            <span>Export Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs">
            RAG Pipeline
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Transform your captured documentation library into RAG vector datasets (JSONL), PDFs, or unified Markdown books.
        </p>
      </div>

      {/* Domain Selector */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="text-sm font-semibold">1. Select Documentation Source</CardTitle>
          <CardDescription className="text-xs">
            Choose which site from your library you wish to export.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-5 pt-0">
          {library.length === 0 ? (
            <div className="text-xs text-muted-foreground italic py-2">
              No documentation libraries found. Capture a documentation site first in the Capture Studio.
            </div>
          ) : (
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-background border border-border text-foreground rounded-lg p-2.5 text-xs focus:ring-1 focus:ring-primary outline-none"
            >
              {library.map((item) => (
                <option key={item.domain} value={item.domain}>
                  {item.domain} ({item.pages || item.pages_count || 0} pages)
                </option>
              ))}
            </select>
          )}
        </CardContent>
      </Card>

      {/* Format Chooser */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="text-sm font-semibold">2. Choose Export Format</CardTitle>
        </CardHeader>
        <CardContent className="p-5 pt-0 grid grid-cols-1 md:grid-cols-3 gap-3">
          {exportFormats.map((f) => {
            const Icon = f.icon
            const isSelected = format === f.id
            return (
              <div
                key={f.id}
                onClick={() => setFormat(f.id)}
                className={`cursor-pointer rounded-lg border p-4 transition-all flex flex-col justify-between gap-3 ${
                  isSelected
                    ? "border-primary bg-primary/5 shadow-xs"
                    : "border-border/60 bg-background/50 hover:border-primary/40"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className={`p-2 rounded-lg ${isSelected ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <Badge variant={isSelected ? "default" : "outline"} className="text-[10px]">
                      {f.badge}
                    </Badge>
                  </div>
                  <h4 className="font-semibold text-xs text-foreground mb-1">{f.title}</h4>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 rounded-xl border border-border/60 bg-card/40 backdrop-blur-sm">
        <div className="text-xs text-muted-foreground">
          Exports are saved to <span className="font-mono text-foreground font-semibold">exports/</span> directory.
        </div>
        <Button
          onClick={handleExport}
          disabled={exporting || !domain}
          className="h-10 px-6 font-medium shadow-xs"
        >
          {exporting ? (
            <span>Exporting dataset...</span>
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
        <Card className="border-emerald-500/30 bg-emerald-500/10 backdrop-blur-sm p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
              <div>
                <h4 className="text-xs font-semibold text-foreground">Export Generated Successfully</h4>
                <p className="text-[11px] text-muted-foreground font-mono truncate max-w-md">
                  {lastExport.path}
                </p>
              </div>
            </div>
            {lastExport.path && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    pyApi.openFile(lastExport.path)
                    toast.info("Opened exported document")
                  }}
                  className="text-xs h-8 border-border bg-background"
                >
                  <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                  Open Document
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    pyApi.openFolder(lastExport.path)
                    toast.info("Opened folder in Explorer")
                  }}
                  className="text-xs h-8 border-border bg-background"
                >
                  <FolderOpen className="h-3.5 w-3.5 mr-1.5" />
                  Show in Explorer
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
