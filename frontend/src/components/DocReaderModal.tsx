import React, { useState, useEffect } from "react"
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Copy, 
  Check, 
  FolderOpen, 
  FileText, 
  Search, 
  BookOpen, 
  Sparkles,
  Layers
} from "lucide-react"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface DocReaderModalProps {
  domain: string | null
  onClose: () => void
}

export const DocReaderModal: React.FC<DocReaderModalProps> = ({ domain, onClose }) => {
  const [docData, setDocData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [selectedFile, setSelectedFile] = useState<string>("book.md")
  const [fileContent, setFileContent] = useState<string>("")
  const [searchFilter, setSearchFilter] = useState<string>("")
  const [copied, setCopied] = useState<boolean>(false)

  useEffect(() => {
    if (!domain) {
      setDocData(null)
      return
    }

    const loadDoc = async () => {
      setLoading(true)
      try {
        const res = await pyApi.getLibraryDoc(domain)
        if (res.success) {
          setDocData(res)
          setFileContent(res.content || "")
          setSelectedFile("book.md")
        } else {
          toast.error(`Failed to load ${domain}: ${res.error}`)
        }
      } catch (err: any) {
        toast.error(`Error loading documentation: ${err.message}`)
      } finally {
        setLoading(false)
      }
    }

    loadDoc()
  }, [domain])

  const handleSelectPage = async (pagePath: string) => {
    setSelectedFile(pagePath)
    if (pagePath === "book.md" && docData) {
      setFileContent(docData.content || "")
      return
    }
    // Read individual subpage
    try {
      // In library bridge, if docData has the path or we read directly
      setFileContent(`# ${pagePath}\n\nLoading page content...`)
      // If we need to fetch specific file content:
      // For now if content is in doc or loaded
    } catch (e) {}
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(fileContent)
    setCopied(true)
    toast.success("Copied markdown to clipboard")
    setTimeout(() => setCopied(false), 2000)
  }

  const handleOpenFolder = () => {
    if (docData?.folder) {
      pyApi.openFolder(docData.folder)
      toast.info("Opened folder in Windows Explorer")
    }
  }

  const pages = docData?.pages || []
  const filteredPages = pages.filter((p: any) => 
    p.path.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (p.title && p.title.toLowerCase().includes(searchFilter.toLowerCase()))
  )

  return (
    <Dialog open={!!domain} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl h-[85vh] flex flex-col p-0 gap-0 overflow-hidden bg-zinc-950 border-white/15">
        {/* Header */}
        <DialogHeader className="flex flex-row items-center justify-between border-b border-white/10 px-6 py-4 space-y-0">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-500/20 text-cyan-400 border border-cyan-500/30">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-bold text-white flex items-center gap-2">
                <span>{domain}</span>
                <Badge variant="default" className="text-[10px] bg-cyan-500/20 text-cyan-400">
                  {docData?.pages?.length || 0} Pages
                </Badge>
              </DialogTitle>
              <p className="text-xs text-muted-foreground">In-App Document Reader & Page Inspector</p>
            </div>
          </div>

          <div className="flex items-center gap-2 pr-6">
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenFolder}
              className="h-8 gap-1.5 text-xs text-zinc-300 hover:text-white border-white/15"
            >
              <FolderOpen className="h-3.5 w-3.5 text-yellow-400" />
              <span>Explorer</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="h-8 gap-1.5 text-xs text-zinc-300 hover:text-white border-white/15"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? "Copied" : "Copy Markdown"}</span>
            </Button>
          </div>
        </DialogHeader>

        {/* Content Split Area */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar / Page Tree */}
          <div className="w-72 border-r border-white/10 bg-zinc-900/40 flex flex-col">
            <div className="p-3 border-b border-white/10">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  placeholder="Filter pages..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="h-8 pl-8 text-xs bg-black/40 border-white/10"
                />
              </div>
            </div>

            <ScrollArea className="flex-1 p-2">
              <div className="space-y-1">
                <button
                  onClick={() => handleSelectPage("book.md")}
                  className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors ${
                    selectedFile === "book.md"
                      ? "bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-500/30"
                      : "text-zinc-300 hover:bg-white/5"
                  }`}
                >
                  <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                  <span className="truncate">Full Unified (book.md)</span>
                </button>

                {filteredPages.map((p: any) => (
                  <button
                    key={p.path}
                    onClick={() => handleSelectPage(p.path)}
                    className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors ${
                      selectedFile === p.path
                        ? "bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-500/30"
                        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                    }`}
                  >
                    <FileText className="h-3.5 w-3.5 shrink-0 opacity-70" />
                    <span className="truncate">{p.title || p.path}</span>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* Markdown Content Viewer */}
          <div className="flex-1 flex flex-col bg-zinc-950/60 overflow-hidden">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-2.5 bg-black/20 text-xs text-muted-foreground font-mono">
              <div className="flex items-center gap-2">
                <Layers className="h-3.5 w-3.5 text-cyan-400" />
                <span className="text-zinc-200">{selectedFile}</span>
              </div>
              <span>{fileContent.length.toLocaleString()} characters</span>
            </div>

            <ScrollArea className="flex-1 p-6">
              {loading ? (
                <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
                  Loading documentation...
                </div>
              ) : (
                <div className="prose prose-invert max-w-none prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-white/10 prose-headings:text-zinc-100 text-zinc-300 text-sm leading-relaxed font-sans whitespace-pre-wrap selection:bg-cyan-500/30">
                  {fileContent}
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
