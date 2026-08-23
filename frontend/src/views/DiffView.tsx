import React, { useState } from "react"
import { GitCompare, Plus, Minus, FileCode, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
  const snapshots = currentItem?.snapshots || []

  const handleCompare = async () => {
    if (!selectedDomain || !v1 || !v2) {
      toast.error("Please select a domain and two snapshots to compare")
      return
    }

    setLoading(true)
    try {
      const res = await pyApi.diffSnapshots(selectedDomain, v1, v2)
      if (res.success) {
        setDiffResult(res)
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
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
            <GitCompare className="h-6 w-6 text-primary" />
            <span>Snapshot Diff Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs">
            Snapshot Engine
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Compare modifications across captured snapshot versions to audit additions, removals, and breaking changes.
        </p>
      </div>

      {/* Selector Bar */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
        <CardContent className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">Documentation Source</label>
              <select
                value={selectedDomain}
                onChange={(e) => {
                  setSelectedDomain(e.target.value)
                  setV1("")
                  setV2("")
                }}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary"
              >
                {library.map((item) => (
                  <option key={item.domain} value={item.domain}>
                    {item.domain} ({item.snapshots?.length || 0} snapshots)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">Base Snapshot (Older)</label>
              <select
                value={v1}
                onChange={(e) => setV1(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="">Select Base Snapshot</option>
                {snapshots.map((s: string) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">Target Snapshot (Newer)</label>
              <select
                value={v2}
                onChange={(e) => setV2(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="">Select Target Snapshot</option>
                {snapshots.map((s: string) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <Button
              onClick={handleCompare}
              disabled={loading || !v1 || !v2}
              className="h-10 font-medium"
            >
              {loading ? "Diffing..." : "Compare Snapshots"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Diff Result Content */}
      {diffResult && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-foreground">File Modifications</h3>
              <Badge variant="outline" className="font-mono text-xs">
                {diffResult.changes?.length || 0} files modified
              </Badge>
            </div>
          </div>

          <div className="space-y-3">
            {diffResult.changes?.map((c: any, idx: number) => (
              <Card key={idx} className="border-border/60 bg-card/60 backdrop-blur-sm overflow-hidden">
                <div className="flex items-center justify-between border-b border-border/50 bg-muted/30 px-4 py-2.5">
                  <div className="flex items-center gap-2 font-mono text-xs text-foreground font-semibold">
                    <FileCode className="h-4 w-4 text-primary" />
                    <span>{c.file}</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <span className="text-emerald-500 font-semibold">+{c.lines_added || 0}</span>
                    <span className="text-destructive font-semibold">-{c.lines_removed || 0}</span>
                  </div>
                </div>

                <div className="p-4 font-mono text-xs bg-background/50 overflow-x-auto">
                  <pre className="text-foreground leading-relaxed">{c.diff_text}</pre>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
