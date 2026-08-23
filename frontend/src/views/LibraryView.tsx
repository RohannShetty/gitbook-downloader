import React, { useState } from "react"
import { 
  Library, 
  Search, 
  BookOpen, 
  FolderOpen, 
  Trash2, 
  FileUp, 
  Layers, 
  Calendar, 
  HardDrive, 
  Sparkles,
  ExternalLink
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatBytes } from "@/lib/utils"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface LibraryViewProps {
  library: any[]
  loading: boolean
  onRefresh: () => void
  onOpenDocReader: (domain: string) => void
  onSelectExport: (domain: string) => void
}

export const LibraryView: React.FC<LibraryViewProps> = ({
  library,
  loading,
  onRefresh,
  onOpenDocReader,
  onSelectExport
}) => {
  const [filter, setFilter] = useState<string>("")

  const filtered = library.filter((item) =>
    item.domain.toLowerCase().includes(filter.toLowerCase()) ||
    (item.provider && item.provider.toLowerCase().includes(filter.toLowerCase()))
  )

  const handleDelete = async (domain: string) => {
    if (confirm(`Are you sure you want to delete ${domain} from library?`)) {
      try {
        await pyApi.deleteDomain(domain)
        toast.success(`Removed ${domain} from library`)
        onRefresh()
      } catch (err: any) {
        toast.error(`Delete failed: ${err.message}`)
      }
    }
  }

  const handleOpenFolder = (folderPath: string) => {
    if (folderPath) {
      pyApi.openFolder(folderPath)
      toast.info("Opened storage folder in Explorer")
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-sky-500/20 text-cyan-400">
              Storage Engine
            </Badge>
            <span className="text-xs text-zinc-400">Local Markdown & Snapshot Repository</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Library className="h-6 w-6 text-cyan-400" />
            <span>Document Library</span>
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search library domains..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-9 h-9 text-xs bg-black/40 border-white/10"
            />
          </div>
          <Button variant="outline" size="sm" onClick={onRefresh} className="h-9 border-white/15 text-xs">
            Refresh
          </Button>
        </div>
      </div>

      {/* Library Table / Card Grid */}
      {loading ? (
        <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
          Loading library entries...
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-white/10 bg-zinc-950/40 p-12 text-center">
          <div className="flex h-12 w-12 mx-auto items-center justify-center rounded-xl bg-white/5 text-zinc-400 mb-4">
            <Library className="h-6 w-6" />
          </div>
          <h3 className="text-base font-semibold text-zinc-200">No documentation sources found</h3>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto mt-1">
            Capture a documentation website from the Capture Studio to build your local offline library.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => (
            <Card
              key={item.domain}
              className="border-white/10 bg-zinc-950/70 hover:border-cyan-500/40 transition-all flex flex-col justify-between group shadow-md"
            >
              <CardHeader className="p-5 pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-500/10 text-cyan-400 border border-cyan-500/20 group-hover:scale-105 transition-transform">
                      <BookOpen className="h-4 w-4" />
                    </div>
                    <div className="overflow-hidden">
                      <h4 className="font-semibold text-sm text-zinc-100 truncate font-mono" title={item.domain}>
                        {item.domain}
                      </h4>
                      <Badge variant="outline" className="text-[10px] uppercase font-mono tracking-wider h-4 px-1 border-white/10 text-zinc-400">
                        {item.provider || "gitbook"}
                      </Badge>
                    </div>
                  </div>

                  <Badge variant="default" className="text-[10px] bg-cyan-500/15 text-cyan-300 font-mono">
                    {item.pages_count || 0} pages
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="p-5 pt-0 space-y-4">
                {/* Meta details */}
                <div className="grid grid-cols-2 gap-2 text-[11px] text-zinc-400 pt-2 border-t border-white/5">
                  <div className="flex items-center gap-1.5 truncate">
                    <HardDrive className="h-3.5 w-3.5 text-zinc-500" />
                    <span>{formatBytes(item.size_bytes || 0)}</span>
                  </div>
                  <div className="flex items-center gap-1.5 truncate">
                    <Layers className="h-3.5 w-3.5 text-zinc-500" />
                    <span>{item.snapshots?.length || 1} Snapshots</span>
                  </div>
                  <div className="col-span-2 flex items-center gap-1.5 truncate text-zinc-500">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{item.last_crawled || "Recently captured"}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2 border-t border-white/10">
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => onOpenDocReader(item.domain)}
                    className="flex-1 h-8 text-xs font-semibold gap-1.5 shadow-sm"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Read</span>
                  </Button>

                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => onSelectExport(item.domain)}
                    className="h-8 w-8 text-zinc-300 hover:text-cyan-400 border-white/15"
                    title="Export to RAG / PDF / JSONL"
                  >
                    <FileUp className="h-3.5 w-3.5" />
                  </Button>

                  {item.folder && (
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleOpenFolder(item.folder)}
                      className="h-8 w-8 text-zinc-300 hover:text-yellow-400 border-white/15"
                      title="Open in Windows Explorer"
                    >
                      <FolderOpen className="h-3.5 w-3.5" />
                    </Button>
                  )}

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(item.domain)}
                    className="h-8 w-8 text-zinc-500 hover:text-rose-400"
                    title="Delete domain"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
