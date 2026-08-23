import React, { useState, useEffect } from "react"
import { Activity, Cpu, HardDrive, ShieldCheck, Terminal, FolderOpen, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

export const DiagnosticsView: React.FC = () => {
  const [sysInfo, setSysInfo] = useState<any>(null)
  const [diagInfo, setDiagInfo] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const loadDiagnostics = async () => {
    setLoading(true)
    try {
      const [sys, diag] = await Promise.all([
        pyApi.getSystemInfo(),
        pyApi.getDiagnostics()
      ])
      setSysInfo(sys)
      setDiagInfo(diag)
    } catch (e: any) {
      toast.error(`Diagnostics error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDiagnostics()
  }, [])

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
              <Activity className="h-6 w-6 text-primary" />
              <span>Diagnostics & Runtime</span>
            </h1>
            <Badge variant="secondary" className="font-mono text-xs">
              System Telemetry
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Engine Health, System Diagnostics, and Runtime Environment Info.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadDiagnostics}
          disabled={loading}
          className="h-9 gap-1.5 text-xs"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Environment Card */}
        <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Cpu className="h-4 w-4 text-primary" />
              <span>Runtime Environment</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-3 text-xs">
            <div className="flex items-center justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">Application Version</span>
              <Badge variant="outline" className="font-mono border-primary/30 text-primary bg-primary/5">
                v{sysInfo?.version || "9.0.0"}
              </Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">Python Engine</span>
              <span className="font-mono text-foreground">{sysInfo?.python || "3.11.x"}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">Operating System Platform</span>
              <span className="font-mono text-foreground capitalize">{sysInfo?.platform || "Windows (win32)"}</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-muted-foreground">WebView GUI Backend</span>
              <span className="font-mono text-emerald-500">Microsoft Edge WebView2</span>
            </div>
          </CardContent>
        </Card>

        {/* Storage Card */}
        <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-primary" />
              <span>Storage Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-3 text-xs">
            <div className="flex flex-col gap-1 py-2 border-b border-border/50">
              <span className="text-muted-foreground">Library Root Directory</span>
              <span className="font-mono text-foreground break-all text-[11px] bg-muted/40 p-2 rounded">
                {sysInfo?.library_dir || "~/.gitbook-downloader/docs"}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-muted-foreground">Output Contract</span>
              <Badge variant="secondary" className="font-mono text-[10px]">
                Markdown + LLMs.txt
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
