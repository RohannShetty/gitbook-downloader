import React, { useState, useEffect, useRef, useMemo } from "react"
import { 
  Download, 
  Play, 
  Square, 
  Sparkles, 
  Terminal, 
  Clock, 
  FileCheck, 
  AlertCircle, 
  Layers, 
  ChevronDown, 
  Copy, 
  Trash2, 
  FolderOpen, 
  CheckCircle2, 
  Plus, 
  ListOrdered, 
  Globe,
  Search,
  BookOpen,
  ArrowRight,
  ExternalLink,
  ShieldAlert,
  RotateCcw,
  Zap,
  Activity,
  Lock,
  Unlock,
  Sliders,
  Cpu,
  Check
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import { pyApi, CaptureProgressPayload, CaptureDonePayload } from "@/lib/bridge"
import { toast } from "sonner"

interface CaptureStudioProps {
  onCaptureCompleted: () => void
  onOpenDocReader: (domain: string) => void
}

interface LogEntry {
  id: string
  time: string
  level: "info" | "downloaded" | "discovered" | "error" | "warn" | "written"
  url?: string
  title?: string
  message: string
}

export const CaptureStudio: React.FC<CaptureStudioProps> = ({
  onCaptureCompleted,
  onOpenDocReader
}) => {
  const [url, setUrl] = useState<string>("")
  const [detecting, setDetecting] = useState<boolean>(false)
  const [detectedProvider, setDetectedProvider] = useState<string | null>(null)
  const [detectedVersions, setDetectedVersions] = useState<string[]>([])
  const [selectedVersions, setSelectedVersions] = useState<string[]>([])

  // Options
  const [maxPages, setMaxPages] = useState<number | string>("")
  const [workers, setWorkers] = useState<number>(5)
  const [pathScope, setPathScope] = useState<string>("")
  const [excludePaths, setExcludePaths] = useState<string>("")
  const [outputMode, setOutputMode] = useState<string>("library")

  // Batch Queue
  const [batchUrls, setBatchUrls] = useState<string[]>([])
  const [newBatchUrl, setNewBatchUrl] = useState<string>("")
  const [activeTab, setActiveTab] = useState<string>("single")

  // In-flight Capture State
  const [isCapturing, setIsCapturing] = useState<boolean>(false)
  const [isComplete, setIsComplete] = useState<boolean>(false)
  const [captureError, setCaptureError] = useState<string | null>(null)
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [discoveredCount, setDiscoveredCount] = useState<number>(0)
  const [downloadedCount, setDownloadedCount] = useState<number>(0)
  const [failedCount, setFailedCount] = useState<number>(0)
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0)
  const [lastDomain, setLastDomain] = useState<string>("")

  // Lock State & Banner
  const [lockStatus, setLockStatus] = useState<any>(null)
  const [checkingLock, setCheckingLock] = useState<boolean>(false)

  // Logs & Filters
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [logFilter, setLogFilter] = useState<"all" | "downloaded" | "discovered" | "error">("all")
  const [logSearch, setLogSearch] = useState<string>("")
  const [autoScroll, setAutoScroll] = useState<boolean>(true)
  const [copiedLogs, setCopiedLogs] = useState<boolean>(false)
  
  const timerRef = useRef<any>(null)
  const logScrollRef = useRef<HTMLDivElement>(null)

  // Check lock status
  const refreshLockStatus = async (targetDomain?: string) => {
    setCheckingLock(true)
    try {
      const res = await pyApi.getLockStatus(targetDomain || url)
      if (res && res.success) {
        setLockStatus(res)
      }
    } catch {
      // Ignore
    } finally {
      setCheckingLock(false)
    }
  }

  useEffect(() => {
    refreshLockStatus()
  }, [])

  // Auto-detect URL provider on typing / pasting
  useEffect(() => {
    const trimmed = url.trim()
    if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
      setDetectedProvider(null)
      setDetectedVersions([])
      return
    }

    refreshLockStatus(trimmed)

    const timer = setTimeout(async () => {
      setDetecting(true)
      try {
        const res = await pyApi.detect(trimmed)
        if (res.success || res.detected) {
          setDetectedProvider(res.provider || "generic")
          setDetectedVersions(res.site_versions || [])
          setSelectedVersions(res.site_versions || [])
        } else {
          setDetectedProvider(null)
        }
      } catch {
        setDetectedProvider(null)
      } finally {
        setDetecting(false)
      }
    }, 350)

    return () => clearTimeout(timer)
  }, [url])

  // Setup Global Bridge Callback Handlers
  useEffect(() => {
    window.onCaptureProgress = (data: CaptureProgressPayload) => {
      if (typeof data.discovered === "number") setDiscoveredCount(data.discovered)
      if (typeof data.downloaded === "number") setDownloadedCount(data.downloaded)
      if (typeof data.failed === "number") setFailedCount(data.failed)
      if (typeof data.percent === "number") setProgressPercent(Math.min(100, Math.max(0, data.percent)))

      const now = new Date().toLocaleTimeString()
      let level: LogEntry["level"] = "info"
      if (data.kind === "downloaded") level = "downloaded"
      else if (data.kind === "discovered") level = "discovered"
      else if (data.kind === "failed") level = "error"
      else if (data.kind === "written") level = "written"

      const msg = data.message || (data.title ? `Downloaded: ${data.title}` : data.url || "Processing...")

      setLogs((prev) => [
        ...prev,
        {
          id: Math.random().toString(36).substring(2, 9),
          time: now,
          level,
          url: data.url,
          title: data.title,
          message: msg
        }
      ])
    }

    window.onCaptureDone = (data: CaptureDonePayload) => {
      setIsCapturing(false)
      clearInterval(timerRef.current)
      refreshLockStatus()

      if (data.success) {
        setIsComplete(true)
        setCaptureError(null)
        setProgressPercent(100)
        toast.success(`Documentation capture complete! ${data.pages_downloaded || 0} pages saved to Library.`)
      } else {
        setIsComplete(false)
        if (data.cancelled) {
          toast.warning("Capture canceled by user.")
          setCaptureError("Capture was cancelled before finishing.")
        } else {
          const err = data.error || "Capture encountered an error."
          setCaptureError(err)
          toast.error(`Capture failed: ${err}`)
        }
      }

      onCaptureCompleted()
    }

    return () => {
      window.onCaptureProgress = undefined
      window.onCaptureDone = undefined
    }
  }, [onCaptureCompleted])

  // Auto-scroll logs
  useEffect(() => {
    if (autoScroll && logScrollRef.current) {
      logScrollRef.current.scrollTop = logScrollRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const handleStartCapture = async (targetUrl?: string) => {
    const crawlUrl = (targetUrl || url).trim()
    if (!crawlUrl) {
      toast.error("Please enter a valid documentation URL")
      return
    }

    try {
      const u = new URL(crawlUrl)
      setLastDomain(u.hostname.replace("www.", ""))
    } catch {
      setLastDomain(crawlUrl)
    }

    setIsCapturing(true)
    setIsComplete(false)
    setCaptureError(null)
    setProgressPercent(0)
    setDiscoveredCount(0)
    setDownloadedCount(0)
    setFailedCount(0)
    setElapsedSeconds(0)
    setLogs([])

    // Start timer
    clearInterval(timerRef.current)
    const startTime = Date.now()
    timerRef.current = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    const options: any = {
      max_pages: maxPages ? parseInt(String(maxPages), 10) : null,
      workers: workers || 5,
      path_scope: pathScope.trim() || null,
      exclude_paths: excludePaths.trim() || null,
      output_mode: outputMode || "library",
      site_versions: selectedVersions.length > 0 ? selectedVersions : null,
    }

    try {
      const res = await pyApi.startCapture(crawlUrl, options)
      if (!res.success) {
        toast.error(`Could not start capture: ${res.error}`)
        setIsCapturing(false)
        setCaptureError(res.error)
        clearInterval(timerRef.current)
        refreshLockStatus(crawlUrl)
      } else {
        toast.info("Crawl engine started in background")
      }
    } catch (err: any) {
      toast.error(`Error: ${err.message}`)
      setIsCapturing(false)
      setCaptureError(err.message)
      clearInterval(timerRef.current)
      refreshLockStatus(crawlUrl)
    }
  }

  const handleCancelCapture = async () => {
    toast.warning("Aborting capture thread...")
    try {
      await pyApi.cancelCapture()
    } catch {
      // Ignore
    }
    setIsCapturing(false)
    clearInterval(timerRef.current)
    setTimeout(() => refreshLockStatus(), 600)
  }

  const handleForceReset = async () => {
    try {
      const res = await pyApi.resetCapture()
      if (res.success) {
        toast.success(`Cleared capture state and released ${res.cleared_locks ?? 0} active lock(s).`)
        setCaptureError(null)
        setIsCapturing(false)
        clearInterval(timerRef.current)
        refreshLockStatus()
      } else {
        toast.error("Failed to reset capture state.")
      }
    } catch (err: any) {
      toast.error(`Error resetting: ${err.message}`)
    }
  }

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      if (text) setUrl(text.trim())
    } catch {
      toast.error("Could not read clipboard")
    }
  }

  const handleAddBatch = () => {
    if (newBatchUrl.trim()) {
      setBatchUrls((prev) => [...prev, newBatchUrl.trim()])
      setNewBatchUrl("")
      toast.success("Added URL to batch queue")
    }
  }

  const handleRemoveBatch = (index: number) => {
    setBatchUrls((prev) => prev.filter((_, i) => i !== index))
  }

  // Filtered log entries
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (logFilter === "downloaded" && log.level !== "downloaded") return false
      if (logFilter === "discovered" && log.level !== "discovered") return false
      if (logFilter === "error" && log.level !== "error") return false
      if (logSearch.trim()) {
        const q = logSearch.toLowerCase()
        return log.message.toLowerCase().includes(q) || (log.url && log.url.toLowerCase().includes(q))
      }
      return true
    })
  }, [logs, logFilter, logSearch])

  const speedPagesPerSec = elapsedSeconds > 0 && downloadedCount > 0 
    ? (downloadedCount / elapsedSeconds).toFixed(1) 
    : "0.0"

  const hasActiveLocks = lockStatus?.has_active_locks || lockStatus?.domain_locked
  const activeLockList = lockStatus?.active_locks || []

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto w-full animate-in fade-in-50 duration-300">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Download className="h-6 w-6 text-primary" />
              <span>Capture Studio</span>
            </h1>
            <Badge variant="outline" className="text-xs font-mono font-medium border-primary/30 text-primary bg-primary/10">
              v9.0 Engine
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Turn GitBook, Docusaurus, ReadTheDocs, Mintlify, and generic SPA documentation websites into clean offline Markdown & RAG vector datasets.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
            <TabsList className="grid grid-cols-2 w-[220px] bg-muted/60">
              <TabsTrigger value="single" className="text-xs">
                Single URL
              </TabsTrigger>
              <TabsTrigger value="batch" className="text-xs">
                Batch ({batchUrls.length})
              </TabsTrigger>
            </TabsList>
          </Tabs>

          <Button
            variant="outline"
            size="sm"
            onClick={handleForceReset}
            className="h-9 gap-1.5 text-xs border-border/80 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-colors"
            title="Force clear active locks and background threads"
          >
            <Zap className="h-3.5 w-3.5 text-amber-500" />
            <span className="hidden sm:inline">Force Reset</span>
          </Button>
        </div>
      </div>

      {/* Active Lock Notification Banner */}
      {hasActiveLocks && (
        <Card className="border-amber-500/40 bg-amber-500/10 backdrop-blur-md shadow-sm animate-in slide-in-from-top-2 duration-300">
          <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-amber-500/20 text-amber-500 flex items-center justify-center shrink-0 border border-amber-500/30">
                <Lock className="h-5 w-5" />
              </div>
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-foreground">
                    Active Storage Lock Detected
                  </h3>
                  <Badge variant="outline" className="text-[10px] border-amber-500/40 text-amber-500 bg-amber-500/5 font-mono">
                    {activeLockList.length} Lock{activeLockList.length > 1 ? "s" : ""}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {activeLockList.map((l: any) => `${l.domain} (PID: ${l.pid || '?'}, ${l.age_seconds || 0}s ago)`).join(", ")}
                  {" — captures to this domain will serialize safely."}
                </p>
              </div>
            </div>

            <Button
              size="sm"
              onClick={handleForceReset}
              className="bg-amber-600 hover:bg-amber-700 text-white text-xs h-8 px-3 gap-1.5 shadow-sm shrink-0 interactive-scale"
            >
              <Unlock className="h-3.5 w-3.5" />
              <span>Unlock & Force Reset</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Main URL Input Card */}
      {activeTab === "single" ? (
        <Card className="glass-card shadow-sm border-border/70">
          <CardContent className="p-6 flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row items-stretch gap-3">
              <div className="relative flex-1">
                <Globe className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="https://pi.dev/docs/latest or https://docs.openalgo.in/ or https://mintlify.com/docs"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !isCapturing && handleStartCapture()}
                  disabled={isCapturing}
                  className="pl-10 pr-24 h-12 bg-background/80 text-sm text-foreground focus-visible:ring-2 focus-visible:ring-primary/40 rounded-lg font-mono placeholder:font-sans"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handlePaste}
                  disabled={isCapturing}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 h-8 px-2.5 text-xs text-muted-foreground hover:text-foreground interactive-scale"
                >
                  <Copy className="h-3.5 w-3.5 mr-1" />
                  Paste
                </Button>
              </div>

              {isCapturing ? (
                <Button
                  variant="destructive"
                  onClick={handleCancelCapture}
                  className="h-12 px-6 font-semibold shadow-sm bg-destructive hover:bg-destructive/90 text-white animate-pulse interactive-scale"
                >
                  <Square className="h-4 w-4 mr-2 fill-current" />
                  Cancel Capture
                </Button>
              ) : (
                <Button
                  onClick={() => handleStartCapture()}
                  disabled={!url.trim()}
                  className="h-12 px-7 font-semibold bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20 interactive-scale"
                >
                  <Play className="h-4 w-4 mr-2 fill-current" />
                  Start Capture
                </Button>
              )}
            </div>

            {/* Provider & Scoping Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs border-t border-border/40">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-muted-foreground font-medium">Provider:</span>
                {detecting ? (
                  <Badge variant="secondary" className="animate-pulse bg-muted/60 text-muted-foreground">
                    Detecting Engine...
                  </Badge>
                ) : detectedProvider ? (
                  <Badge variant="secondary" className="capitalize font-semibold text-primary border-primary/20 bg-primary/10 gap-1 shadow-xs">
                    <Sparkles className="h-3 w-3" />
                    {detectedProvider}
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground font-normal">
                    Auto-detects on URL entry
                  </Badge>
                )}

                {detectedVersions.length > 0 && (
                  <div className="flex items-center gap-1.5 ml-2">
                    <span className="text-muted-foreground font-medium">Versions:</span>
                    {detectedVersions.map((v) => (
                      <Badge 
                        key={v} 
                        variant={selectedVersions.includes(v) ? "default" : "outline"}
                        className="cursor-pointer text-[10px] py-0.5 px-2 font-mono transition-all interactive-scale"
                        onClick={() => {
                          if (selectedVersions.includes(v)) {
                            setSelectedVersions(selectedVersions.filter(x => x !== v))
                          } else {
                            setSelectedVersions([...selectedVersions, v])
                          }
                        }}
                      >
                        {v}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className="text-muted-foreground">Concurrency:</span>
                  <select
                    value={workers}
                    onChange={(e) => setWorkers(Number(e.target.value))}
                    disabled={isCapturing}
                    className="bg-background border border-border text-foreground text-xs rounded-md px-2.5 py-1 focus:ring-1 focus:ring-primary outline-none font-medium"
                  >
                    <option value={1}>1 worker (safe)</option>
                    <option value={3}>3 workers</option>
                    <option value={5}>5 workers (balanced)</option>
                    <option value={8}>8 workers (fast)</option>
                    <option value={12}>12 workers (turbo)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Advanced Scoping Accordion */}
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="options" className="border-none">
                <AccordionTrigger className="py-1 text-xs text-muted-foreground hover:text-foreground hover:no-underline">
                  <div className="flex items-center gap-1.5 font-medium">
                    <Sliders className="h-3.5 w-3.5 text-primary" />
                    <span>Advanced Scoping, Limits & Output Routing</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-3 pb-1">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs text-muted-foreground font-medium">Path Scope (prefixes)</label>
                      <Input
                        placeholder="/docs, /api"
                        value={pathScope}
                        onChange={(e) => setPathScope(e.target.value)}
                        disabled={isCapturing}
                        className="h-8 text-xs bg-background font-mono"
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs text-muted-foreground font-medium">Exclude Paths (substrings)</label>
                      <Input
                        placeholder="/blog, /changelog"
                        value={excludePaths}
                        onChange={(e) => setExcludePaths(e.target.value)}
                        disabled={isCapturing}
                        className="h-8 text-xs bg-background font-mono"
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs text-muted-foreground font-medium">Max Pages Limit</label>
                      <Input
                        type="number"
                        placeholder="e.g. 500 (blank = all)"
                        value={maxPages}
                        onChange={(e) => setMaxPages(e.target.value)}
                        disabled={isCapturing}
                        className="h-8 text-xs bg-background font-mono"
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs text-muted-foreground font-medium">Output Mode</label>
                      <select
                        value={outputMode}
                        onChange={(e) => setOutputMode(e.target.value)}
                        disabled={isCapturing}
                        className="h-8 bg-background border border-border text-foreground text-xs rounded-md px-2 focus:ring-1 focus:ring-primary outline-none"
                      >
                        <option value="library">Library Only (~/.gitbook-downloader)</option>
                        <option value="both">Both (Library + Local Folder)</option>
                        <option value="local">Local Folder Only (./domain-docs)</option>
                      </select>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      ) : (
        /* Batch Queue Manager */
        <Card className="glass-card shadow-sm border-border/70">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <ListOrdered className="h-4 w-4 text-primary" />
              Batch Capture Queue
            </CardTitle>
            <CardDescription className="text-xs">
              Add multiple documentation targets to download sequentially into your Library.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex gap-2">
              <Input
                placeholder="https://docs.site2.com/"
                value={newBatchUrl}
                onChange={(e) => setNewBatchUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddBatch()}
                className="h-9 text-xs bg-background font-mono"
              />
              <Button size="sm" onClick={handleAddBatch} className="h-9 px-4 interactive-scale">
                <Plus className="h-3.5 w-3.5 mr-1" />
                Add
              </Button>
            </div>

            {batchUrls.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted-foreground border border-dashed rounded-lg bg-muted/10">
                No URLs in queue. Enter links above to run sequential batch captures.
              </div>
            ) : (
              <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1">
                {batchUrls.map((bUrl, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 border border-border/50 text-xs">
                    <div className="flex items-center gap-2 overflow-hidden">
                      <span className="text-muted-foreground font-mono text-[10px]">#{idx + 1}</span>
                      <span className="font-mono truncate">{bUrl}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveBatch(idx)}
                      className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Progress & Live Telemetry Section */}
      {(isCapturing || isComplete || captureError || logs.length > 0) && (
        <div className="flex flex-col gap-4 animate-in fade-in-50 duration-300">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Radial Gauge Card */}
            <Card className={`glass-card shadow-sm transition-all duration-300 ${
              isComplete ? "border-emerald-500/40 glow-emerald" : captureError ? "border-destructive/40 glow-rose" : isCapturing ? "border-primary/40 glow-cyan" : ""
            }`}>
              <CardContent className="p-5 flex flex-col items-center justify-center text-center gap-3">
                <div className="relative flex items-center justify-center w-28 h-28">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      stroke="currentColor"
                      strokeWidth="8"
                      className="text-muted/20"
                      fill="transparent"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      stroke="currentColor"
                      strokeWidth="8"
                      strokeDasharray={251.2}
                      strokeDashoffset={251.2 - (251.2 * progressPercent) / 100}
                      strokeLinecap="round"
                      className={`transition-all duration-500 ${
                        isComplete ? "text-emerald-500" : captureError ? "text-destructive" : "text-primary"
                      }`}
                      fill="transparent"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold tracking-tight text-foreground font-mono">
                      {isComplete ? "100%" : `${progressPercent}%`}
                    </span>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                      {isComplete ? "COMPLETE" : isCapturing ? "CRAWLING" : captureError ? "ERROR" : "READY"}
                    </span>
                  </div>
                </div>

                <div className="w-full flex flex-col gap-1">
                  <Progress 
                    value={progressPercent} 
                    className="h-2 rounded-full overflow-hidden bg-muted/40"
                    indicatorClassName={isComplete ? "bg-emerald-500" : captureError ? "bg-destructive" : "bg-primary animate-shimmer"}
                  />
                  <div className="flex justify-between text-[11px] text-muted-foreground pt-1 font-mono">
                    <span>{downloadedCount} / {discoveredCount || downloadedCount} pages</span>
                    <span>{speedPagesPerSec} p/s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stat Card 1: Discovered URLs */}
            <Card className="glass-card shadow-sm">
              <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Discovered URLs</CardTitle>
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  <Globe className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground font-mono">{discoveredCount}</div>
                <p className="text-[11px] text-muted-foreground mt-1">Sitemap & DOM link frontier</p>
              </CardContent>
            </Card>

            {/* Stat Card 2: Downloaded Pages */}
            <Card className="glass-card shadow-sm">
              <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Downloaded Pages</CardTitle>
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                  <FileCheck className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground font-mono">{downloadedCount}</div>
                <p className="text-[11px] text-muted-foreground mt-1">Normalized Markdown artifacts</p>
              </CardContent>
            </Card>

            {/* Stat Card 3: Elapsed Time & Health */}
            <Card className="glass-card shadow-sm">
              <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Elapsed Time</CardTitle>
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-500">
                  <Clock className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground font-mono">{elapsedSeconds}s</div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  {failedCount > 0 ? `${failedCount} skipped / error pages` : "Optimal socket throughput"}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Success Banner */}
          {isComplete && (
            <Card className="border-emerald-500/30 bg-emerald-500/10 backdrop-blur-md shadow-sm animate-in fade-in-50 duration-300">
              <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center shrink-0 border border-emerald-500/30">
                    <CheckCircle2 className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">Documentation Capture Successful!</h3>
                    <p className="text-xs text-muted-foreground">
                      Successfully synthesized {downloadedCount} pages into Markdown book, page tree, and llms.txt.
                    </p>
                  </div>
                </div>
                {lastDomain && (
                  <Button 
                    size="sm" 
                    onClick={() => onOpenDocReader(lastDomain)}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm interactive-scale shrink-0"
                  >
                    <BookOpen className="h-3.5 w-3.5 mr-1.5" />
                    Read in Studio
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Error Banner */}
          {captureError && (
            <Card className="border-destructive/40 bg-destructive/10 backdrop-blur-md shadow-sm animate-in fade-in-50 duration-300">
              <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-destructive/20 text-destructive flex items-center justify-center shrink-0 border border-destructive/30">
                    <ShieldAlert className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-destructive">Capture Notice</h3>
                    <p className="text-xs text-muted-foreground font-mono break-all mt-0.5">{captureError}</p>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button 
                    size="sm" 
                    variant="destructive"
                    onClick={handleForceReset}
                    className="bg-destructive hover:bg-destructive/90 text-white shadow-sm interactive-scale"
                  >
                    <Zap className="h-3.5 w-3.5 mr-1.5" />
                    Force Reset
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleStartCapture()}
                    className="border-destructive/30 hover:bg-destructive/20 interactive-scale"
                  >
                    <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
                    Retry
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Filterable Live Crawl Terminal */}
          <Card className="glass-card shadow-sm overflow-hidden border-border/70">
            <div className="p-3.5 border-b border-border/50 bg-muted/20 flex flex-wrap items-center justify-between gap-2.5">
              <div className="flex items-center gap-2.5">
                <div className="relative flex items-center">
                  <span className={`h-2.5 w-2.5 rounded-full ${isCapturing ? 'bg-emerald-500 animate-pulse' : 'bg-muted-foreground/50'}`} />
                  {isCapturing && <span className="absolute h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping opacity-75" />}
                </div>
                <div className="flex items-center gap-1.5">
                  <Terminal className="h-4 w-4 text-primary" />
                  <span className="text-xs font-semibold text-foreground">Live Telemetry Terminal</span>
                </div>
                <Badge variant="outline" className="text-[10px] py-0 px-1.5 h-4 font-mono border-border text-muted-foreground">
                  {logs.length} events
                </Badge>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center gap-1 bg-background/60 p-0.5 rounded-lg border border-border/40">
                <Button
                  variant={logFilter === "all" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setLogFilter("all")}
                  className="h-6 text-[11px] px-2 rounded-md font-medium"
                >
                  All ({logs.length})
                </Button>
                <Button
                  variant={logFilter === "downloaded" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setLogFilter("downloaded")}
                  className="h-6 text-[11px] px-2 rounded-md font-medium text-emerald-500"
                >
                  Downloaded ({logs.filter(l => l.level === "downloaded").length})
                </Button>
                <Button
                  variant={logFilter === "discovered" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setLogFilter("discovered")}
                  className="h-6 text-[11px] px-2 rounded-md font-medium text-primary"
                >
                  Discovered ({logs.filter(l => l.level === "discovered").length})
                </Button>
                <Button
                  variant={logFilter === "error" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setLogFilter("error")}
                  className="h-6 text-[11px] px-2 rounded-md font-medium text-destructive"
                >
                  Errors ({logs.filter(l => l.level === "error").length})
                </Button>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                  <Input
                    placeholder="Search logs..."
                    value={logSearch}
                    onChange={(e) => setLogSearch(e.target.value)}
                    className="h-7 text-[11px] pl-6 pr-2 w-32 sm:w-40 bg-background/70 font-mono"
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const text = logs.map(l => `[${l.time}] [${l.level.toUpperCase()}] ${l.message}`).join("\n")
                    navigator.clipboard.writeText(text)
                    setCopiedLogs(true)
                    toast.success("Copied terminal logs to clipboard")
                    setTimeout(() => setCopiedLogs(false), 2000)
                  }}
                  className="h-7 px-2.5 text-xs border-border/70 interactive-scale"
                  title="Copy terminal logs"
                >
                  {copiedLogs ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setLogs([])}
                  className="h-7 px-2.5 text-xs text-muted-foreground hover:text-destructive border-border/70 interactive-scale"
                  title="Clear terminal"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Log Stream Window */}
            <div 
              ref={logScrollRef}
              className="h-72 overflow-y-auto p-4 font-mono text-xs flex flex-col gap-1.5 bg-background/60 leading-relaxed select-text"
            >
              {filteredLogs.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-xs italic">
                  {logs.length === 0 
                    ? "Ready for capture. Real-time discovered URLs and downloaded pages will stream here." 
                    : "No log entries match the current filter criteria."}
                </div>
              ) : (
                filteredLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-2 py-0.5 border-b border-border/20 last:border-none">
                    <span className="text-muted-foreground/70 text-[10px] select-none shrink-0 pt-0.5">[{log.time}]</span>
                    {log.level === "downloaded" && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-emerald-500/40 text-emerald-500 bg-emerald-500/10 shrink-0 font-mono">
                        DOWNLOADED
                      </Badge>
                    )}
                    {log.level === "discovered" && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-primary/40 text-primary bg-primary/10 shrink-0 font-mono">
                        DISCOVERED
                      </Badge>
                    )}
                    {log.level === "error" && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-destructive/40 text-destructive bg-destructive/10 shrink-0 font-mono">
                        ERROR
                      </Badge>
                    )}
                    {log.level === "written" && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-emerald-400/40 text-emerald-400 bg-emerald-400/10 shrink-0 font-mono">
                        WRITTEN
                      </Badge>
                    )}
                    {log.level === "info" && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-border text-muted-foreground shrink-0 font-mono">
                        INFO
                      </Badge>
                    )}
                    <span className={`break-all ${
                      log.level === "downloaded" ? "text-foreground font-medium" :
                      log.level === "discovered" ? "text-primary/90" :
                      log.level === "error" ? "text-destructive font-medium" :
                      "text-muted-foreground"
                    }`}>
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
