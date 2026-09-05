import React, { useState, useMemo } from "react"
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
  RefreshCw, 
  ArrowUpDown, 
  FileCode, 
  Check,
  Pencil,
  Edit3,
  X
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

type SortField = "date" | "pages" | "name" | "size"

export const LibraryView: React.FC<LibraryViewProps> = ({
  library,
  loading,
  onRefresh,
  onOpenDocReader,
  onSelectExport
}) => {
  const [filter, setFilter] = useState<string>("")
  const [sortBy, setSortBy] = useState<SortField>("date")
  const [renamingDomain, setRenamingDomain] = useState<string | null>(null)
  const [renameInput, setRenameInput] = useState<string>("")
  const [isRenaming, setIsRenaming] = useState<boolean>(false)

  const filteredAndSorted = useMemo(() => {
    const q = filter.toLowerCase().trim()
    const list = library.filter((item) =>
      (item.domain || "").toLowerCase().includes(q) ||
      (item.provider || "").toLowerCase().includes(q) ||
      (item.title || "").toLowerCase().includes(q)
    )

    return list.sort((a, b) => {
      if (sortBy === "date") {
        return (b.last_crawled || "").localeCompare(a.last_crawled || "")
      }
      if (sortBy === "pages") {
        return (b.pages || 0) - (a.pages || 0)
      }
      if (sortBy === "size") {
        return (b.size_bytes || 0) - (a.size_bytes || 0)
      }
      if (sortBy === "name") {
        return (a.domain || "").localeCompare(b.domain || "")
      }
      return 0
    })
  }, [library, filter, sortBy])

  const handleStartRename = (domain: string) => {
    setRenamingDomain(domain)
    setRenameInput(domain)
  }

  const handleSaveRename = async () => {
    if (!renamingDomain) return
    const target = renameInput.trim()
    if (!target) {
      toast.error("Project name cannot be empty")
      return
    }
    if (target === renamingDomain) {
      setRenamingDomain(null)
      return
    }

    setIsRenaming(true)
    try {
      const res = await pyApi.renameDomain(renamingDomain, target)
      if (res.success) {
        toast.success(`Renamed '${renamingDomain}' to '${target}'`)
        setRenamingDomain(null)
        onRefresh()
      } else {
        toast.error(`Rename failed: ${res.error || "Unknown error"}`)
      }
    } catch (err: any) {
      toast.error(`Rename failed: ${err.message}`)
    } finally {
      setIsRenaming(false)
    }
  }

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

  const getProviderBadgeStyle = (provider: string) => {
    const p = (provider || "").toLowerCase()
    if (p.includes("gitbook")) return "border-sky-500/30 text-sky-700 bg-sky-500/10 dark:text-sky-400"
    if (p.includes("mintlify")) return "border-teal-500/30 text-teal-700 bg-teal-500/10 dark:text-teal-400"
    if (p.includes("docusaurus")) return "border-emerald-500/30 text-emerald-700 bg-emerald-500/10 dark:text-emerald-400"
    if (p.includes("readthedocs")) return "border-blue-500/30 text-blue-700 bg-blue-500/10 dark:text-blue-400"
    return "border-purple-500/30 text-purple-700 bg-purple-500/10 dark:text-purple-400"
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-7xl mx-auto w-full space-y-6 animate-in fade-in-50 duration-300">
      {/* Rename Dialog Modal */}
      {renamingDomain && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="relative w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl backdrop-blur-xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Edit3 className="h-5 w-5 text-primary" />
                <h3 className="text-base font-semibold text-foreground">Rename Documentation Project</h3>
              </div>
              <button
                onClick={() => setRenamingDomain(null)}
                className="rounded-lg p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <p className="text-xs text-muted-foreground mb-4">
              Enter a new folder/domain identifier for <span className="font-mono text-foreground font-semibold">{renamingDomain}</span>. This updates your local storage and search index.
            </p>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-foreground mb-1.5 block">
                  New Project Identifier
                </label>
                <Input
                  value={renameInput}
                  onChange={(e) => setRenameInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSaveRename()
                    if (e.key === "Escape") setRenamingDomain(null)
                  }}
                  autoFocus
                  placeholder="e.g. docs.myproject.com or my-framework-docs"
                  className="font-mono text-xs h-9"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRenamingDomain(null)}
                  disabled={isRenaming}
                  className="h-8 text-xs"
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSaveRename}
                  disabled={isRenaming || !renameInput.trim()}
                  className="h-8 text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  {isRenaming ? "Renaming..." : "Save Name"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Library className="h-6 w-6 text-primary" />
              <span>Document Library</span>
            </h1>
            <Badge variant="secondary" className="font-mono text-xs border border-border bg-muted/60">
              {library.length} doc sets
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Browse offline Markdown documentation, snapshots, and RAG datasets saved on this machine.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Filter library..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-9 h-9 text-xs bg-background/80 font-mono"
            />
          </div>

          <div className="flex items-center gap-1.5 bg-background/80 border border-border p-1 rounded-lg">
            <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortField)}
              className="bg-transparent text-foreground text-xs outline-none cursor-pointer pr-1"
            >
              <option value="date">Sort: Recent</option>
              <option value="pages">Sort: Page Count</option>
              <option value="size">Sort: Size</option>
              <option value="name">Sort: Domain</option>
            </select>
          </div>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRefresh} 
            className="h-9 px-3 text-xs border-border interactive-scale"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Library Grid */}
      {loading ? (
        <div className="flex h-64 items-center justify-center text-sm text-muted-foreground font-mono">
          Loading library entries...
        </div>
      ) : filteredAndSorted.length === 0 ? (
        <Card className="glass-card p-12 text-center border-dashed border-border/80">
          <div className="flex h-14 w-14 mx-auto items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4 border border-primary/20">
            <Library className="h-7 w-7" />
          </div>
          <h3 className="text-base font-semibold text-foreground">No documentation sources found</h3>
          <p className="text-xs text-muted-foreground max-w-md mx-auto mt-1.5 leading-relaxed">
            {filter ? `No library items match "${filter}". Clear your search query to see all sets.` : "Capture documentation from the Capture Studio to build your offline library."}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAndSorted.map((item) => {
            const pageCount = item.pages ?? item.pages_count ?? 0
            const folderPath = item.path || item.folder || ""
            return (
              <Card
                key={item.domain}
                className="glass-card flex flex-col justify-between group shadow-sm hover:border-primary/50"
              >
                <CardHeader className="p-5 pb-3">
                  <div className="flex items-start justify-between gap-2.5">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary border border-primary/20 group-hover:scale-105 transition-transform">
                        <BookOpen className="h-4 w-4" />
                      </div>
                      <div className="overflow-hidden">
                        <h4 className="font-semibold text-sm text-foreground truncate font-mono" title={item.domain}>
                          {item.title && item.title !== item.domain ? item.title : item.domain}
                        </h4>
                        <div className="flex items-center gap-1.5 mt-1">
                          <span className="text-[11px] text-muted-foreground font-mono truncate max-w-[130px]">{item.domain}</span>
                          <Badge variant="outline" className={`text-[9px] uppercase font-mono tracking-wider h-4 px-1.5 py-0 ${getProviderBadgeStyle(item.provider)}`}>
                            {item.provider || "generic"}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <Badge variant="secondary" className="text-[11px] font-mono shrink-0 bg-muted/60">
                      {pageCount} pages
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="p-5 pt-0 space-y-4">
                  {/* Meta details */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-muted-foreground pt-3 border-t border-border/40">
                    <div className="flex items-center gap-1.5 truncate">
                      <HardDrive className="h-3.5 w-3.5 text-muted-foreground/70" />
                      <span className="font-mono">{formatBytes(item.size_bytes || 0)}</span>
                    </div>
                    <div className="flex items-center gap-1.5 truncate">
                      <Layers className="h-3.5 w-3.5 text-muted-foreground/70" />
                      <span>{item.snapshot_count || item.snapshots?.length || 1} Snapshots</span>
                    </div>
                    <div className="col-span-2 flex items-center gap-1.5 truncate text-[10px] text-muted-foreground/80">
                      <Calendar className="h-3.5 w-3.5 text-muted-foreground/70" />
                      <span>{item.last_crawled || "Recently captured"}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-3 border-t border-border/40">
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => onOpenDocReader(item.domain)}
                      className="flex-1 h-8 text-xs font-medium gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90 shadow-xs interactive-scale"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>Read in Studio</span>
                    </Button>

                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleStartRename(item.domain)}
                      className="h-8 w-8 text-muted-foreground hover:text-foreground border-border interactive-scale"
                      title="Rename project"
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>

                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => onSelectExport(item.domain)}
                      className="h-8 w-8 text-muted-foreground hover:text-foreground border-border interactive-scale"
                      title="Export to RAG / PDF / JSONL"
                    >
                      <FileUp className="h-3.5 w-3.5" />
                    </Button>

                    {folderPath && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleOpenFolder(folderPath)}
                        className="h-8 w-8 text-muted-foreground hover:text-foreground border-border interactive-scale"
                        title="Open in Windows Explorer"
                      >
                        <FolderOpen className="h-3.5 w-3.5" />
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(item.domain)}
                      className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 interactive-scale"
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
