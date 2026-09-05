import React, { useState } from "react"
import { GitCompare, Plus, Minus, FileCode, Check, Layers, ArrowRight, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface DiffViewProps {
  library: any[]
}

export const DiffView: React.FC<DiffViewProps> = ({ library }) => {
  const [selectedDomain, setSelectedDomain] = useState<string>(library[0]?.domain || "")
  const [v1, setV1] = useState<string>("")
  const [v2, setV2] = useState<string>("")
  const [diffResult, setDiffResult] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const currentItem = library.find((item) => item.domain === selectedDomain)
  const snapshots = (currentItem?.snapshots && currentItem.snapshots.length > 0)
    ? currentItem.snapshots
    : []

  const handleCompare = async () => {
    if (!selectedDomain || !v1 || !v2) {
      toast.error("Please select a domain and two snapshot versions to compare")
      return
    }

    setLoading(true)
    try {
      const res = await pyApi.diffSnapshots(selectedDomain, v1, v2)
      if (res.success) {
        setDiffResult(res)
        toast.success(`Computed diff for ${selectedDomain}`)
      } else {
        toast.error(`Diff failed: ${res.error}`)
      }
    } catch (err: any) {
      toast.error(`Diff error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6 animate-in fade-in-50 duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <GitCompare className="h-6 w-6 text-primary" />
            <span>Snapshot Diff Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs border border-border bg-muted/60">
            SemVer Versioning
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Compare modifications across captured snapshot versions to audit additions, removals, and breaking changes in documentation.
        </p>
      </div>

      {/* Selector Bar */}
      <Card className="glass-card shadow-sm">
        <CardContent className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3.5 items-end">
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block font-medium">Documentation Source</label>
              <select
                value={selectedDomain}
                onChange={(e) => {
                  setSelectedDomain(e.target.value)
                  setV1("")
                  setV2("")
                }}
                className="h-10 w-full rounded-lg border border-border bg-background/80 px-3 text-xs text-foreground outline-none focus:ring-2 focus:ring-primary/40 font-mono"
              >
                {library.map((item) => (
                  <option key={item.domain} value={item.domain}>
                    {item.domain} ({item.snapshot_count || item.snapshots?.length || 1} v)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block font-medium">Base Snapshot (Older)</label>
              <select
                value={v1}
                onChange={(e) => setV1(e.target.value)}
                className="h-10 w-full rounded-lg border border-border bg-background/80 px-3 text-xs text-foreground outline-none focus:ring-2 focus:ring-primary/40 font-mono"
              >
                <option value="">Select Base Snapshot</option>
                {snapshots.map((s: any) => {
                  const val = typeof s === "string" ? s : (s.version || s.version_id || "?")
                  return (
                    <option key={val} value={val}>
                      {val}
                    </option>
                  )
                })}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block font-medium">Target Snapshot (Newer)</label>
              <select
                value={v2}
                onChange={(e) => setV2(e.target.value)}
                className="h-10 w-full rounded-lg border border-border bg-background/80 px-3 text-xs text-foreground outline-none focus:ring-2 focus:ring-primary/40 font-mono"
              >
                <option value="">Select Target Snapshot</option>
                {snapshots.map((s: any) => {
                  const val = typeof s === "string" ? s : (s.version || s.version_id || "?")
                  return (
                    <option key={val} value={val}>
                      {val}
                    </option>
                  )
                })}
              </select>
            </div>

            <Button
              onClick={handleCompare}
              disabled={loading || !v1 || !v2}
              className="h-10 font-semibold bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20 interactive-scale"
            >
              {loading ? "Diffing..." : "Compare Snapshots"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Diff Result Content */}
      {diffResult && (
        <div className="space-y-4 animate-in fade-in-50 duration-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-foreground">File Modifications</h3>
              <Badge variant="outline" className="font-mono text-xs border-border bg-muted/50">
                {diffResult.changes?.length || 0} change sets
              </Badge>
            </div>
            <div className="flex items-center gap-3 font-mono text-xs">
              <span className="text-emerald-700 dark:text-emerald-500 font-semibold">+{diffResult.lines_added || 0} added</span>
              <span className="text-destructive font-semibold">-{diffResult.lines_removed || 0} removed</span>
            </div>
          </div>

          <div className="space-y-3">
            {diffResult.changes?.map((c: any, idx: number) => (
              <Card key={idx} className="glass-card overflow-hidden shadow-sm">
                <div className="flex items-center justify-between border-b border-border/50 bg-muted/30 px-4 py-2.5">
                  <div className="flex items-center gap-2 font-mono text-xs text-foreground font-semibold">
                    <FileCode className="h-4 w-4 text-primary" />
                    <span>{c.url || c.file || "docs.md"}</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <span className="text-emerald-700 dark:text-emerald-500 font-semibold">+{c.lines_added || 0}</span>
                    <span className="text-destructive font-semibold">-{c.lines_removed || 0}</span>
                  </div>
                </div>

                <div className="p-4 font-mono text-xs bg-background/70 overflow-x-auto select-text leading-relaxed">
                  {c.diff_text ? (
                    <div className="flex flex-col gap-0.5">
                      {c.diff_text.split("\n").map((line: string, lIdx: number) => {
                        const isAdd = line.startsWith("+") && !line.startsWith("+++")
                        const isDel = line.startsWith("-") && !line.startsWith("---")
                        const isHdr = line.startsWith("@@")
                        return (
                          <div
                            key={lIdx}
                            className={`px-1.5 py-0.5 rounded font-mono ${
                              isAdd ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400" :
                              isDel ? "bg-destructive/15 text-destructive" :
                              isHdr ? "text-primary/80 font-bold bg-primary/5" :
                              "text-muted-foreground"
                            }`}
                          >
                            {line}
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-muted-foreground italic">No textual differences found between snapshots.</div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
