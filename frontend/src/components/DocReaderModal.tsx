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
import { MarkdownViewer } from "@/components/MarkdownViewer"

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

  const handleSelectPage = async (pageTarget: any) => {
    if (pageTarget === "book.md" || (typeof pageTarget === "object" && pageTarget.relpath === "book.md")) {
      setSelectedFile("book.md")
      setFileContent(docData?.content || docData?.book_content || "")
      return
    }

    const filePath = typeof pageTarget === "string" ? pageTarget : (pageTarget.path || pageTarget.relpath)
    const relPath = typeof pageTarget === "string" ? pageTarget : (pageTarget.relpath || pageTarget.path)
    setSelectedFile(relPath)

    try {
      const res = await pyApi.readFile(filePath)
      if (res.success) {
        setFileContent(res.content || "")
      } else {
        toast.error(`Could not read page: ${res.error}`)
      }
    } catch (err: any) {
      toast.error(`Error reading page: ${err.message}`)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(fileContent)
    setCopied(true)
    toast.success("Copied markdown to clipboard")
    setTimeout(() => setCopied(false), 2000)
  }

  const handleOpenFolder = () => {
    if (docData?.folder || docData?.path) {
      pyApi.openFolder(docData.folder || docData.path)
      toast.info("Opened folder in Windows Explorer")
    }
  }

  const pages = docData?.pages || []
  const filteredPages = pages.filter((p: any) => 
    (p.path || p.relpath || "").toLowerCase().includes(searchFilter.toLowerCase()) ||
    (p.title && p.title.toLowerCase().includes(searchFilter.toLowerCase()))
  )

  return (
    <Dialog open={!!domain} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl h-[85vh] flex flex-col p-0 gap-0 overflow-hidden bg-card border-border">
        {/* Header */}
        <DialogHeader className="flex flex-row items-center justify-between border-b border-border px-6 py-4 space-y-0">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-bold text-foreground flex items-center gap-2">
                <span>{domain}</span>
                <Badge variant="secondary" className="text-[10px] font-mono">
                  {docData?.pages?.length || 0} Pages
                </Badge>
              </DialogTitle>
              <p className="text-xs text-muted-foreground">In-App Document Reader & Page Inspector</p>
            </div>
          </div>

          <div className="flex items-center gap-2 pr-6">
            {(docData?.folder || docData?.path) && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleOpenFolder}
                className="h-8 gap-1.5 text-xs border-border"
              >
                <FolderOpen className="h-3.5 w-3.5" />
                <span>Explorer</span>
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="h-8 gap-1.5 text-xs border-border"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? "Copied" : "Copy Markdown"}</span>
            </Button>
          </div>
        </DialogHeader>

        {/* Content Split Area */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar / Page Tree */}
          <div className="w-72 border-r border-border bg-muted/20 flex flex-col">
            <div className="p-3 border-b border-border">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  placeholder="Filter pages..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="h-8 pl-8 text-xs bg-background"
                />
              </div>
            </div>

            <ScrollArea className="flex-1 p-2">
              <div className="space-y-1">
                <button
                  onClick={() => handleSelectPage("book.md")}
                  className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors ${
                    selectedFile === "book.md"
                      ? "bg-primary/10 text-primary font-semibold border border-primary/20"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  <Sparkles className="h-3.5 w-3.5 text-primary" />
                  <span className="truncate">Full Unified (book.md)</span>
                </button>

                {filteredPages.map((p: any) => {
                  const pPath = p.relpath || p.path
                  return (
                    <button
                      key={pPath}
                      onClick={() => handleSelectPage(p)}
                      className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors ${
                        selectedFile === pPath
                          ? "bg-primary/10 text-primary font-semibold border border-primary/20"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      }`}
                    >
                      <FileText className="h-3.5 w-3.5 shrink-0 opacity-70" />
                      <span className="truncate">{p.title || pPath}</span>
                    </button>
                  )
                })}
              </div>
            </ScrollArea>
          </div>

          {/* Markdown Content Viewer */}
          <div className="flex-1 flex flex-col bg-background overflow-hidden">
            {loading ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                Loading documentation...
              </div>
            ) : (
              <MarkdownViewer
                content={fileContent}
                title={selectedFile}
                domain={domain || undefined}
                onExportPdf={() => {
                  if (docData?.domain) {
                    pyApi.exportDoc(docData.domain, "pdf").then((res) => {
                      if (res.success) toast.success(`PDF exported to: ${res.path}`)
                    }).catch((err) => toast.error(`PDF export failed: ${err.message}`))
                  }
                }}
              />
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
