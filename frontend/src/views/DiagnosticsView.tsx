import React, { useState, useEffect } from "react"
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Folder, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  ShieldCheck, 
  Terminal,
  Lock,
  Unlock,
  Zap,
  Info
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

export const DiagnosticsView: React.FC = () => {
  const [sysInfo, setSysInfo] = useState<any>(null)
  const [diagnostics, setDiagnostics] = useState<any>(null)
  const [lockStatus, setLockStatus] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [sys, diag, locks] = await Promise.all([
        pyApi.getSystemInfo(),
        pyApi.getDiagnostics(),
        pyApi.getLockStatus()
      ])
      setSysInfo(sys)
      setDiagnostics(diag)
      setLockStatus(locks)
    } catch (err: any) {
      toast.error(`Error loading diagnostics: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleClearLocks = async () => {
    try {
      const res = await pyApi.resetCapture()
      if (res.success) {
        toast.success(`Cleared all locks (${res.cleared_locks ?? 0} released).`)
        fetchData()
      } else {
        toast.error("Failed to clear locks.")
      }
    } catch (err: any) {
      toast.error(`Error clearing locks: ${err.message}`)
    }
  }

  const activeLocks = lockStatus?.active_locks || []

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6 animate-in fade-in-50 duration-300">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Activity className="h-6 w-6 text-primary" />
              <span>System & Diagnostics</span>
            </h1>
            <Badge variant="secondary" className="font-mono text-xs border border-border bg-muted/60">
              Engine Health
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time telemetry, storage lock inspection, environment specifications, and audit reports.
          </p>
        </div>

        <Button 
          variant="outline" 
          size="sm" 
          onClick={fetchData}
          className="h-9 px-3 text-xs border-border interactive-scale"
        >
          <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* System Info */}
        <Card className="glass-card shadow-sm">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Cpu className="h-4 w-4 text-primary" />
              <span>Runtime Environment</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-2.5 text-xs">
            <div className="flex items-center justify-between py-1.5 border-b border-border/40">
              <span className="text-muted-foreground">App Version</span>
              <span className="font-mono font-semibold text-foreground">{sysInfo?.version || "11.0.6"}</span>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-border/40">
              <span className="text-muted-foreground">Python Runtime</span>
              <span className="font-mono text-foreground">{sysInfo?.python || "3.13.x"}</span>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-border/40">
              <span className="text-muted-foreground">Platform / OS</span>
              <span className="font-mono text-foreground">{sysInfo?.platform || "win32"}</span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-muted-foreground">Storage Root</span>
              <span className="font-mono text-foreground truncate max-w-[220px]" title={sysInfo?.library_dir}>
                {sysInfo?.library_dir || "~/.gitbook-downloader"}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Lock Inspector */}
        <Card className="glass-card shadow-sm">
          <CardHeader className="p-5 pb-3 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Lock className="h-4 w-4 text-amber-600 dark:text-amber-500" />
              <span>Storage Locks Inspector</span>
            </CardTitle>
            {activeLocks.length > 0 && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleClearLocks}
                className="h-7 text-[11px] px-2.5 gap-1 interactive-scale"
              >
                <Unlock className="h-3 w-3" />
                Clear All Locks
              </Button>
            )}
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-2 text-xs">
            {activeLocks.length === 0 ? (
              <div className="flex items-center gap-2 py-4 text-emerald-700 dark:text-emerald-500 justify-center font-medium bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                <CheckCircle2 className="h-4 w-4" />
                <span>All storage domains unlocked and healthy</span>
              </div>
            ) : (
              <div className="space-y-2">
                {activeLocks.map((l: any, i: number) => (
                  <div key={i} className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-between">
                    <div>
                      <div className="font-mono font-semibold text-foreground">{l.domain}</div>
                      <div className="text-[11px] text-muted-foreground">
                        PID: {l.pid || "?"} | Age: {l.age_seconds || 0}s | {l.is_stale ? "Stale / Orphaned" : "Active Lock"}
                      </div>
                    </div>
                    <Badge variant="outline" className={`text-[10px] ${l.is_stale ? "text-destructive border-destructive/40" : "text-amber-700 border-amber-500/40 dark:text-amber-500"}`}>
                      {l.is_stale ? "Stale" : "Active"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Last Run Diagnostics */}
      <Card className="glass-card shadow-sm">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Terminal className="h-4 w-4 text-primary" />
            <span>Last Capture Run Audit</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Diagnostics details reported by the v9 crawler engine.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-5 pt-0">
          {!diagnostics || Object.keys(diagnostics).length === 0 ? (
            <div className="text-xs text-muted-foreground italic py-6 text-center bg-muted/20 rounded-lg border border-dashed border-border/60">
              No previous capture runs recorded in this session.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-background/60 border border-border/50">
                <span className="text-muted-foreground block text-[11px] mb-1">Target URL</span>
                <span className="font-mono text-foreground font-semibold break-all">{diagnostics.url || "N/A"}</span>
              </div>
              <div className="p-3 rounded-lg bg-background/60 border border-border/50">
                <span className="text-muted-foreground block text-[11px] mb-1">Detected Provider</span>
                <span className="font-mono text-primary font-semibold capitalize">{diagnostics.provider || "N/A"}</span>
              </div>
              <div className="p-3 rounded-lg bg-background/60 border border-border/50">
                <span className="text-muted-foreground block text-[11px] mb-1">Pages Captured</span>
                <span className="font-mono text-emerald-700 dark:text-emerald-500 font-semibold">{diagnostics.pages_captured || 0} pages ({diagnostics.duration_s || 0}s)</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
