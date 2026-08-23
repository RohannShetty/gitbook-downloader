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
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-rose-500/20 text-rose-400 border-rose-500/30">
              System Telemetry
            </Badge>
            <span className="text-xs text-zinc-400">Engine Health & System Diagnostics</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Activity className="h-6 w-6 text-rose-400" />
            <span>Diagnostics & Runtime</span>
          </h1>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadDiagnostics}
          disabled={loading}
          className="h-9 gap-1.5 text-xs border-white/15 text-zinc-300 hover:text-white"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Environment Card */}
        <Card className="border-white/10 bg-zinc-950/70">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
              <Cpu className="h-4 w-4 text-cyan-400" />
              <span>Runtime Environment</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-3 text-xs">
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-zinc-400">Application Version</span>
              <Badge variant="default" className="font-mono bg-cyan-500/20 text-cyan-300">
                v{sysInfo?.version || "9.0.0-beta.1"}
              </Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-zinc-400">Python Engine</span>
              <span className="font-mono text-zinc-200">{sysInfo?.python || "3.11.x"}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-zinc-400">Operating System Platform</span>
              <span className="font-mono text-zinc-200 capitalize">{sysInfo?.platform || "Windows (win32)"}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-zinc-400">WebView GUI Backend</span>
              <span className="font-mono text-emerald-400">Microsoft Edge WebView2</span>
            </div>
          </CardContent>
        </Card>

        {/* Storage Card */}
        <Card className="border-white/10 bg-zinc-950/70">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-amber-400" />
              <span>Storage Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0 space-y-3 text-xs">
            <div className="py-2 border-b border-white/5 space-y-1">
              <span className="text-zinc-400 block">Library Storage Path</span>
              <span className="font-mono text-zinc-300 text-[11px] break-all block">
                {sysInfo?.library_dir || "C:\\Users\\rohan\\.gitbook-downloader\\docs"}
              </span>
            </div>
            <div className="py-2 border-b border-white/5 space-y-1">
              <span className="text-zinc-400 block">Current Working Directory</span>
              <span className="font-mono text-zinc-300 text-[11px] break-all block">
                {sysInfo?.cwd || "D:\\gitbook-downloader"}
              </span>
            </div>
            <div className="pt-2">
              {sysInfo?.library_dir && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => pyApi.openFolder(sysInfo.library_dir)}
                  className="w-full gap-1.5 text-xs border-white/15"
                >
                  <FolderOpen className="h-3.5 w-3.5 text-yellow-400" />
                  <span>Open Library in Windows Explorer</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Supported Providers Engine */}
        <Card className="border-white/10 bg-zinc-950/70 md:col-span-2">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Supported Documentation Engine Providers</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
              <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                <span className="font-semibold text-cyan-400 block">GitBook</span>
                <span className="text-[11px] text-zinc-400 mt-1 block">API & llms.txt & sitemap stream discovery</span>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                <span className="font-semibold text-sky-400 block">Docusaurus</span>
                <span className="text-[11px] text-zinc-400 mt-1 block">Sitemap xml + DOM parser with versions</span>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                <span className="font-semibold text-purple-400 block">ReadTheDocs</span>
                <span className="text-[11px] text-zinc-400 mt-1 block">Sphinx & mkdocs html parsers</span>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                <span className="font-semibold text-emerald-400 block">Mintlify</span>
                <span className="text-[11px] text-zinc-400 mt-1 block">Modern React SSR doc parsers</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
