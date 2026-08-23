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
  Database
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
      color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
    },
    {
      id: "pdf" as const,
      title: "PDF / Standalone HTML Document",
      icon: FileSpreadsheet,
      desc: "Compiled single-file printable documentation handbook with structured headings, code syntax, and clean reading typography.",
      badge: "Print / Share",
      color: "text-rose-400 border-rose-500/30 bg-rose-500/10",
    },
    {
      id: "md" as const,
      title: "Single Markdown (book.md)",
      icon: FileText,
      desc: "Concatenated Markdown handbook with relative internal link preservation, code blocks, and full TOC table.",
      badge: "Universal MD",
      color: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
    },
  ]

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="default" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
            Export Studio
          </Badge>
          <span className="text-xs text-zinc-400">RAG Pipelines, LLM Embeddings & Printable Handbooks</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <FileUp className="h-6 w-6 text-emerald-400" />
          <span>Export Studio</span>
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Transform your captured documentation library into RAG vector datasets (JSONL), PDFs, or unified Markdown books.
        </p>
      </div>

      {/* Domain Selector */}
      <Card className="border-white/10 bg-zinc-950/70">
        <CardContent className="p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex-1">
              <label className="text-xs text-zinc-400 mb-1.5 block">Select Documentation Source</label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="h-10 w-full rounded-lg border border-white/15 bg-black/60 px-3 text-xs text-zinc-200 font-mono"
              >
                {library.length === 0 && <option value="">No library sources available</option>}
                {library.map((item) => (
                  <option key={item.domain} value={item.domain}>
                    {item.domain} ({item.pages_count || 0} pages)
                  </option>
                ))}
              </select>
            </div>

            <Button
              onClick={handleExport}
              disabled={exporting || !domain}
              className="h-10 px-6 sm:mt-5 font-semibold bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/20"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              <span>{exporting ? "Exporting..." : `Export ${format.toUpperCase()}`}</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Format Picker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {exportFormats.map((fmt) => {
          const Icon = fmt.icon
          const isSelected = format === fmt.id
          return (
            <Card
              key={fmt.id}
              onClick={() => setFormat(fmt.id)}
              className={`cursor-pointer transition-all border p-5 flex flex-col justify-between ${
                isSelected
                  ? "border-emerald-500 bg-emerald-950/20 shadow-lg shadow-emerald-500/10"
                  : "border-white/10 bg-zinc-950/60 hover:border-white/20"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-lg border ${fmt.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <Badge variant="outline" className="text-[10px] border-white/10 text-zinc-400">
                    {fmt.badge}
                  </Badge>
                </div>
                <h3 className="font-semibold text-sm text-white">{fmt.title}</h3>
                <p className="text-xs text-zinc-400 mt-2 leading-relaxed">{fmt.desc}</p>
              </div>

              <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-xs">
                <span className={isSelected ? "text-emerald-400 font-semibold" : "text-zinc-500"}>
                  {isSelected ? "Selected Format" : "Click to select"}
                </span>
                {isSelected && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
              </div>
            </Card>
          )
        })}
      </div>

      {/* Result Card */}
      {lastExport && (
        <Card className="border-emerald-500/40 bg-zinc-950/90 p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-white">Export Generated Successfully</h4>
                <p className="text-xs font-mono text-zinc-400 mt-0.5 break-all">{lastExport.path}</p>
                {lastExport.count && (
                  <p className="text-[11px] text-emerald-400 mt-1">Processed {lastExport.count} page records</p>
                )}
              </div>
            </div>

            {lastExport.path && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => pyApi.openFolder(lastExport.path)}
                className="gap-1.5 text-xs border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/10"
              >
                <FolderOpen className="h-3.5 w-3.5 text-yellow-400" />
                <span>Show in Explorer</span>
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
