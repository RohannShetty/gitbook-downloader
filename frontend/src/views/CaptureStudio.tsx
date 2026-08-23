import React, { useState, useEffect, useRef } from "react"
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
  Globe 
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ScrollArea } from "@/components/ui/scroll-area"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface CaptureStudioProps {
  onCaptureCompleted: () => void
  onOpenDocReader: (domain: string) => void
}

interface LogEntry {
  id: string
  time: string
  level: "info" | "success" | "warn" | "error" | "discover"
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
  const [maxDepth, setMaxDepth] = useState<number | string>("")
  const [workers, setWorkers] = useState<number>(5)
  const [matchPrefix, setMatchPrefix] = useState<string>("")
  const [outputMode, setOutputMode] = useState<string>("both")
  const [includeImages, setIncludeImages] = useState<boolean>(false)

  // Batch Queue
  const [batchUrls, setBatchUrls] = useState<string[]>([])
  const [newBatchUrl, setNewBatchUrl] = useState<string>("")
  const [showBatch, setShowBatch] = useState<boolean>(false)

  // In-flight Capture State
  const [isCapturing, setIsCapturing] = useState<boolean>(false)
  const [isComplete, setIsComplete] = useState<boolean>(false)
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [discoveredCount, setDiscoveredCount] = useState<number>(0)
  const [downloadedCount, setDownloadedCount] = useState<number>(0)
  const [failedCount, setFailedCount] = useState<number>(0)
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0)
  const [lastDoneData, setLastDoneData] = useState<any>(null)

  // Logs
  const [logs, setLogs] = useState<LogEntry[]>([])
  const timerRef = useRef<any>(null)
  const logScrollRef = useRef<HTMLDivElement>(null)

  // Auto-detect URL provider on typing / pasting
  useEffect(() => {
    if (!url.trim().startsWith("http")) {
      setDetectedProvider(null)
      setDetectedVersions([])
      return
    }

    const timer = setTimeout(async () => {
      setDetecting(true)
      try {
        const res = await pyApi.detect(url.trim())
        if (res.detected) {
          setDetectedProvider(res.provider || "generic")
          setDetectedVersions(res.site_versions || [])
          setSelectedVersions(res.site_versions || [])
        } else {
          setDetectedProvider(null)
        }
      } catch (e) {
        setDetectedProvider(null)
      } finally {
        setDetecting(false)
      }
    }, 400)

    return () => clearTimeout(timer)
  }, [url])

  // Setup Global Bridge Callback Handlers
  useEffect(() => {
    window.onCaptureProgress = (data: any) => {
      if (data.discovered !== undefined) setDiscoveredCount(data.discovered)
      if (data.downloaded !== undefined) setDownloadedCount(data.downloaded)
      if (data.failed !== undefined) setFailedCount(data.failed)
      if (data.percent !== undefined) setProgressPercent(Math.min(100, Math.max(0, data.percent)))

      if (data.log) {
        const now = new Date().toLocaleTimeString()
        let level: LogEntry["level"] = "info"
        if (data.log.includes("✅") || data.log.includes("Downloaded")) level = "success"
        else if (data.log.includes("🔍") || data.log.includes("Discovered")) level = "discover"
        else if (data.log.includes("❌") || data.log.includes("Error")) level = "error"
        else if (data.log.includes("⚠️")) level = "warn"

        setLogs((prev) => [
          ...prev,
          { id: Math.random().toString(), time: now, level, message: data.log }
        ])
      }
    }

    window.onCaptureDone = (data: any) => {
      setIsCapturing(false)
      setIsComplete(true)
      setProgressPercent(100)
      setLastDoneData(data)
      clearInterval(timerRef.current)

      if (data.success) {
        toast.success(`Capture complete! ${data.pages_downloaded || 0} pages saved.`)
      } else {
        toast.error(`Capture finished with issues: ${data.error || "Check terminal log"}`)
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
    if (logScrollRef.current) {
      logScrollRef.current.scrollTop = logScrollRef.current.scrollHeight
    }
  }, [logs])

  const handleStartCapture = async () => {
    if (!url.trim()) {
      toast.error("Please enter a documentation URL")
      return
    }

    setIsCapturing(true)
    setIsComplete(false)
    setProgressPercent(0)
    setDiscoveredCount(0)
    setDownloadedCount(0)
    setFailedCount(0)
    setElapsedSeconds(0)
    setLastDoneData(null)
    setLogs([])

    // Start timer
    clearInterval(timerRef.current)
    const startTime = Date.now()
    timerRef.current = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    const options: any = {
      max_pages: maxPages ? parseInt(String(maxPages), 10) : null,
      max_depth: maxDepth ? parseInt(String(maxDepth), 10) : null,
      workers: workers || 5,
      match_prefix: matchPrefix.trim() || null,
      output_mode: outputMode || "both",
      include_images: includeImages,
      selected_versions: selectedVersions.length > 0 ? selectedVersions : null,
    }

    try {
      const res = await pyApi.startCapture(url.trim(), options)
      if (!res.success) {
        toast.error(`Could not start capture: ${res.error}`)
        setIsCapturing(false)
        clearInterval(timerRef.current)
      } else {
        toast.info("Crawl engine started in background")
      }
    } catch (err: any) {
      toast.error(`Error: ${err.message}`)
      setIsCapturing(false)
      clearInterval(timerRef.current)
    }
  }

  const handleCancelCapture = async () => {
    await pyApi.cancelCapture()
    setIsCapturing(false)
    clearInterval(timerRef.current)
    toast.warning("Capture canceled by user")
  }

  const handleAddBatch = () => {
    if (newBatchUrl.trim()) {
      setBatchUrls((prev) => [...prev, newBatchUrl.trim()])
      setNewBatchUrl("")
      toast.success("Added URL to batch queue")
    }
  }

  const handleClearLogs = () => setLogs([])
  const handleCopyLogs = () => {
    const text = logs.map((l) => `[${l.time}] ${l.message}`).join("\n")
    navigator.clipboard.writeText(text)
    toast.success("Logs copied to clipboard")
  }

  // Radial progress calculations (stroke-dashoffset)
  const radius = 48
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (progressPercent / 100) * circumference

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Top Banner / Hero Card */}
      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-sky-500/10 via-zinc-950/80 to-zinc-950 p-6 backdrop-blur-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="default" className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                v9.0 Engine
              </Badge>
              <span className="text-xs text-zinc-400">Universal Documentation Scraper & RAG Parser</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Capture Studio</h1>
            <p className="text-sm text-zinc-400 mt-1 max-w-xl">
              Download complete GitBook, Docusaurus, ReadTheDocs, and Mintlify sites into clean, structured Markdown, PDF, and RAG-ready vector datasets.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBatch(!showBatch)}
              className="border-white/15 gap-1.5 text-xs text-zinc-300 hover:text-white"
            >
              <ListOrdered className="h-3.5 w-3.5 text-cyan-400" />
              <span>{showBatch ? "Hide Batch Queue" : `Batch Queue (${batchUrls.length})`}</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Batch Queue Drawer */}
      {showBatch && (
        <Card className="border-cyan-500/30 bg-black/40">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm flex items-center justify-between">
              <span className="flex items-center gap-2">
                <ListOrdered className="h-4 w-4 text-cyan-400" />
                Batch Documentation Queue
              </span>
              <span className="text-xs text-muted-foreground font-normal">{batchUrls.length} queued</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-2 space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="https://docs.another-service.com/"
                value={newBatchUrl}
                onChange={(e) => setNewBatchUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddBatch()}
                className="text-xs h-9 bg-black/60"
              />
              <Button size="sm" onClick={handleAddBatch} className="gap-1 text-xs">
                <Plus className="h-3.5 w-3.5" />
                <span>Add</span>
              </Button>
            </div>

            {batchUrls.length > 0 && (
              <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                {batchUrls.map((bUrl, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-md bg-white/5 px-3 py-1.5 text-xs">
                    <span className="font-mono text-zinc-300 truncate max-w-md">{bUrl}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setBatchUrls((prev) => prev.filter((_, i) => i !== idx))}
                      className="h-6 w-6 text-zinc-500 hover:text-red-400"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* URL Capture Bar */}
      <Card className="border-white/15 bg-zinc-950/70 shadow-lg">
        <CardContent className="p-5 space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Globe className="absolute left-3.5 top-3 h-4 w-4 text-cyan-400/80" />
              <Input
                placeholder="Enter doc URL (e.g. https://docs.openalgo.in/)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isCapturing}
                className="pl-10 h-11 text-sm bg-black/60 font-mono text-zinc-200 border-white/15 focus-visible:ring-cyan-500/50"
              />
              {detecting && (
                <span className="absolute right-3.5 top-3.5 text-[11px] text-cyan-400 animate-pulse font-sans">
                  Detecting engine...
                </span>
              )}
            </div>

            {!isCapturing ? (
              <Button
                onClick={handleStartCapture}
                className="h-11 px-6 font-semibold gap-2 shadow-cyan-500/20 shadow-lg"
              >
                <Play className="h-4 w-4 fill-current" />
                <span>Start Capture</span>
              </Button>
            ) : (
              <Button
                variant="destructive"
                onClick={handleCancelCapture}
                className="h-11 px-6 font-semibold gap-2"
              >
                <Square className="h-4 w-4 fill-current" />
                <span>Cancel</span>
              </Button>
            )}
          </div>

          {/* Provider Badge & Multi-Version Selector */}
          {detectedProvider && (
            <div className="flex flex-wrap items-center gap-3 pt-1 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="text-zinc-400">Provider:</span>
                <Badge variant="default" className="capitalize bg-cyan-500/20 text-cyan-300 border-cyan-500/40">
                  {detectedProvider}
                </Badge>
              </div>

              {detectedVersions.length > 0 && (
                <div className="flex items-center gap-1.5">
                  <span className="text-zinc-400">Versions:</span>
                  {detectedVersions.map((ver) => {
                    const isSelected = selectedVersions.includes(ver)
                    return (
                      <button
                        key={ver}
                        type="button"
                        onClick={() => {
                          if (isSelected) {
                            setSelectedVersions(selectedVersions.filter((v) => v !== ver))
                          } else {
                            setSelectedVersions([...selectedVersions, ver])
                          }
                        }}
                        className={`rounded px-2 py-0.5 font-mono text-[11px] transition-colors border ${
                          isSelected
                            ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300 font-semibold"
                            : "bg-white/5 border-white/10 text-zinc-500"
                        }`}
                      >
                        {ver}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {/* Advanced Scoping Accordion */}
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="options" className="border-white/10">
              <AccordionTrigger className="text-xs text-zinc-400 hover:text-zinc-200 py-2">
                <span>Advanced Scoping & Crawl Rules</span>
              </AccordionTrigger>
              <AccordionContent className="pt-2">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <label className="text-zinc-400 mb-1 block">Max Pages (Empty = All)</label>
                    <Input
                      type="number"
                      placeholder="e.g. 50"
                      value={maxPages}
                      onChange={(e) => setMaxPages(e.target.value)}
                      className="h-8 text-xs bg-black/40"
                    />
                  </div>
                  <div>
                    <label className="text-zinc-400 mb-1 block">Max Depth</label>
                    <Input
                      type="number"
                      placeholder="e.g. 5"
                      value={maxDepth}
                      onChange={(e) => setMaxDepth(e.target.value)}
                      className="h-8 text-xs bg-black/40"
                    />
                  </div>
                  <div>
                    <label className="text-zinc-400 mb-1 block">Concurrent Workers</label>
                    <Input
                      type="number"
                      value={workers}
                      onChange={(e) => setWorkers(parseInt(e.target.value, 10) || 5)}
                      className="h-8 text-xs bg-black/40"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="text-zinc-400 mb-1 block">Match Prefix Filter</label>
                    <Input
                      placeholder="/api/v1/ or /guides/"
                      value={matchPrefix}
                      onChange={(e) => setMatchPrefix(e.target.value)}
                      className="h-8 text-xs bg-black/40 font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-zinc-400 mb-1 block">Output Format</label>
                    <select
                      value={outputMode}
                      onChange={(e) => setOutputMode(e.target.value)}
                      className="h-8 w-full rounded-md border border-white/15 bg-black/40 px-2 text-xs text-zinc-200"
                    >
                      <option value="both">Both (Single MD + Chunks)</option>
                      <option value="single">Single Markdown (book.md)</option>
                      <option value="chunks">Chunks Directory Only</option>
                    </select>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>

      {/* Real-time Progress & Telemetry Section */}
      {(isCapturing || isComplete) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 60fps Radial Motion Gauge Card */}
          <Card className={`border-white/15 bg-zinc-950/80 transition-all ${isComplete ? "border-emerald-500/40 glow-emerald" : ""}`}>
            <CardHeader className="p-4 pb-0 text-center">
              <CardTitle className="text-sm font-medium text-zinc-300">
                {isComplete ? "Capture Complete" : "Crawl Progress"}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 flex flex-col items-center justify-center">
              <div className="relative flex items-center justify-center">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r={radius}
                    className="stroke-white/10"
                    strokeWidth="8"
                    fill="transparent"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r={radius}
                    className={`transition-all duration-300 ease-out ${
                      isComplete ? "stroke-emerald-400" : "stroke-cyan-400"
                    }`}
                    strokeWidth="8"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    fill="transparent"
                  />
                </svg>

                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className={`text-2xl font-bold font-mono tracking-tight ${isComplete ? "text-emerald-400" : "text-white"}`}>
                    {Math.round(progressPercent)}%
                  </span>
                  <span className={`text-[10px] font-semibold tracking-wider uppercase ${isComplete ? "text-emerald-400" : "text-cyan-400"}`}>
                    {isComplete ? "DONE" : isCapturing ? "STREAMING" : "IDLE"}
                  </span>
                </div>
              </div>

              {/* Striped linear bar */}
              <div className="w-full mt-4">
                <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                  <div
                    className={`h-full transition-all duration-300 ${
                      isComplete
                        ? "bg-emerald-500"
                        : "bg-gradient-to-r from-sky-500 to-cyan-400 animate-shimmer bg-[length:200%_100%]"
                    }`}
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Telemetry 4-Stat Grid */}
          <div className="md:col-span-2 grid grid-cols-2 gap-4">
            <Card className="border-white/10 bg-zinc-950/60 p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground font-medium">Discovered URLs</span>
                <Globe className="h-4 w-4 text-cyan-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-zinc-100 mt-2">{discoveredCount}</div>
              <span className="text-[11px] text-zinc-500">Sitemap & DOM link discovery</span>
            </Card>

            <Card className={`border-white/10 bg-zinc-950/60 p-4 flex flex-col justify-between ${isComplete ? "border-emerald-500/30" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground font-medium">Downloaded Pages</span>
                <FileCheck className={`h-4 w-4 ${isComplete ? "text-emerald-400" : "text-sky-400"}`} />
              </div>
              <div className={`text-3xl font-bold font-mono mt-2 ${isComplete ? "text-emerald-400" : "text-zinc-100"}`}>
                {downloadedCount}
              </div>
              <span className="text-[11px] text-zinc-500">Clean markdown generated</span>
            </Card>

            <Card className="border-white/10 bg-zinc-950/60 p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground font-medium">Failed Pages</span>
                <AlertCircle className="h-4 w-4 text-rose-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-zinc-100 mt-2">{failedCount}</div>
              <span className="text-[11px] text-zinc-500">HTTP errors / 404s</span>
            </Card>

            <Card className="border-white/10 bg-zinc-950/60 p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground font-medium">Elapsed Time</span>
                <Clock className="h-4 w-4 text-amber-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-zinc-100 mt-2">{elapsedSeconds}s</div>
              <span className="text-[11px] text-zinc-500">Multi-worker speed</span>
            </Card>
          </div>
        </div>
      )}

      {/* Completion Banner with Quick Action buttons */}
      {isComplete && lastDoneData && (
        <Card className="border-emerald-500/40 bg-emerald-950/20 p-5 shadow-emerald-950/50 shadow-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Documentation Capture Successful!</h3>
                <p className="text-xs text-zinc-300 mt-0.5">
                  Saved <span className="font-semibold text-emerald-400">{lastDoneData.pages_downloaded || downloadedCount}</span> pages into library.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="emerald"
                size="sm"
                onClick={() => lastDoneData.domain && onOpenDocReader(lastDoneData.domain)}
                className="gap-1.5 text-xs font-semibold"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>Read in Studio</span>
              </Button>
              {lastDoneData.output_dir && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => pyApi.openFolder(lastDoneData.output_dir)}
                  className="gap-1.5 text-xs border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/10"
                >
                  <FolderOpen className="h-3.5 w-3.5 text-yellow-400" />
                  <span>Open Folder</span>
                </Button>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Live Syntax-Highlighted Terminal Console */}
      <Card className="border-white/10 bg-zinc-950/90 shadow-2xl">
        <CardHeader className="flex flex-row items-center justify-between border-b border-white/10 px-4 py-2.5 space-y-0">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-cyan-400" />
            <CardTitle className="text-xs font-medium text-zinc-300 font-mono">Live Crawl Terminal</CardTitle>
            <Badge variant="outline" className="text-[10px] h-4.5 px-1.5 text-zinc-400 border-white/10">
              {logs.length} events
            </Badge>
          </div>

          <div className="flex items-center gap-1.5">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCopyLogs}
              className="h-7 w-7 text-zinc-400 hover:text-zinc-200"
              title="Copy logs"
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClearLogs}
              className="h-7 w-7 text-zinc-400 hover:text-zinc-200"
              title="Clear logs"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div
            ref={logScrollRef}
            className="h-64 overflow-y-auto p-3 font-mono text-[11px] leading-relaxed space-y-1 bg-black/60"
          >
            {logs.length === 0 ? (
              <div className="flex h-full items-center justify-center text-zinc-600 italic">
                Ready for capture. Streamed logs and discovered URLs will appear here...
              </div>
            ) : (
              logs.map((log) => {
                let colorClass = "text-zinc-300"
                if (log.level === "success") colorClass = "text-emerald-400 font-semibold"
                else if (log.level === "discover") colorClass = "text-cyan-400"
                else if (log.level === "error") colorClass = "text-rose-400 font-bold"
                else if (log.level === "warn") colorClass = "text-amber-400"

                return (
                  <div key={log.id} className="flex items-start gap-2 break-all">
                    <span className="text-zinc-600 select-none">[{log.time}]</span>
                    <span className={colorClass}>{log.message}</span>
                  </div>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
