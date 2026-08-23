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
  ExternalLink,
  RefreshCw
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
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
    (item.domain || "").toLowerCase().includes(filter.toLowerCase()) ||
    (item.provider || "").toLowerCase().includes(filter.toLowerCase()) ||
    (item.title || "").toLowerCase().includes(filter.toLowerCase())
  )

  const handleDelete = async (domain: string) => {
    if (confirm(`Are you sure you want to delete ${domain} from your local library?`)) {
      try {
        await pyApi.deleteDomain(domain)
        toast.success(`Removed ${domain} from library`)
        onRefresh()
      } catch (err: any) {
        toast.error(`Delete failed: ${err.message}`)
      }
    }
  }

  const handleOpenFolder = (folderPath?: string) => {
    if (folderPath) {
      pyApi.openFolder(folderPath)
      toast.info("Opened documentation folder in Explorer")
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
              <Library className="h-6 w-6 text-primary" />
              <span>Document Library</span>
            </h1>
            <Badge variant="secondary" className="font-mono text-xs">
              {library.length} sites
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Browse offline Markdown documentation, snapshots, and RAG datasets saved on this machine.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Search library..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-9 h-9 text-xs bg-background"
            />
          </div>
          <Button variant="outline" size="sm" onClick={onRefresh} className="h-9 text-xs">
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
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
        <Card className="border-border/60 bg-card/60 p-12 text-center">
          <div className="flex h-12 w-12 mx-auto items-center justify-center rounded-xl bg-muted text-muted-foreground mb-4">
            <Library className="h-6 w-6" />
          </div>
          <h3 className="text-base font-semibold text-foreground">No documentation sources found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto mt-1">
            Capture a documentation website from the Capture Studio to build your local offline library.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => {
            const pageCount = item.pages ?? item.pages_count ?? 0
            const folderPath = item.path || item.folder || ""
            return (
              <Card
                key={item.domain}
                className="border-border/60 bg-card/60 backdrop-blur-sm hover:border-primary/40 transition-all flex flex-col justify-between group shadow-sm"
              >
                <CardHeader className="p-5 pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5 overflow-hidden">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20 group-hover:scale-105 transition-transform">
                        <BookOpen className="h-4 w-4" />
                      </div>
                      <div className="overflow-hidden">
                        <h4 className="font-semibold text-sm text-foreground truncate font-mono" title={item.domain}>
                          {item.title && item.title !== item.domain ? item.title : item.domain}
                        </h4>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className="text-[11px] text-muted-foreground font-mono truncate max-w-[140px]">{item.domain}</span>
                          <Badge variant="outline" className="text-[9px] uppercase font-mono tracking-wider h-3.5 px-1 py-0 border-border text-muted-foreground">
                            {item.provider || "generic"}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <Badge variant="secondary" className="text-[11px] font-mono shrink-0">
                      {pageCount} pages
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="p-5 pt-0 space-y-4">
                  {/* Meta details */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-muted-foreground pt-3 border-t border-border/50">
                    <div className="flex items-center gap-1.5 truncate">
                      <HardDrive className="h-3.5 w-3.5" />
                      <span>{formatBytes(item.size_bytes || 0)}</span>
                    </div>
                    <div className="flex items-center gap-1.5 truncate">
                      <Layers className="h-3.5 w-3.5" />
                      <span>{item.snapshot_count || item.snapshots?.length || 1} Snapshots</span>
                    </div>
                    <div className="col-span-2 flex items-center gap-1.5 truncate text-[10px]">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>{item.last_crawled || "Recently captured"}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-3 border-t border-border/50">
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => onOpenDocReader(item.domain)}
                      className="flex-1 h-8 text-xs font-medium gap-1.5 shadow-xs"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>Read</span>
                    </Button>

                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => onSelectExport(item.domain)}
                      className="h-8 w-8 text-muted-foreground hover:text-foreground"
                      title="Export to RAG / PDF / JSONL"
                    >
                      <FileUp className="h-3.5 w-3.5" />
                    </Button>

                    {folderPath && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleOpenFolder(folderPath)}
                        className="h-8 w-8 text-muted-foreground hover:text-foreground"
                        title="Open in Windows Explorer"
                      >
                        <FolderOpen className="h-3.5 w-3.5" />
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(item.domain)}
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      title="Delete domain"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
