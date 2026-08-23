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
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="default" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
            Snapshot Engine
          </Badge>
          <span className="text-xs text-zinc-400">Documentation Change Tracking & Changelog Diffing</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <GitCompare className="h-6 w-6 text-purple-400" />
          <span>Snapshot Diff Studio</span>
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Compare modifications across captured snapshot versions to audit additions, removals, and breaking changes.
        </p>
      </div>

      {/* Selector Bar */}
      <Card className="border-white/10 bg-zinc-950/70">
        <CardContent className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Documentation Source</label>
              <select
                value={selectedDomain}
                onChange={(e) => {
                  setSelectedDomain(e.target.value)
                  setV1("")
                  setV2("")
                }}
                className="h-10 w-full rounded-lg border border-white/15 bg-black/60 px-3 text-xs text-zinc-200"
              >
                {library.map((item) => (
                  <option key={item.domain} value={item.domain}>
                    {item.domain} ({item.snapshots?.length || 0} snapshots)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Base Snapshot (Older)</label>
              <select
                value={v1}
                onChange={(e) => setV1(e.target.value)}
                className="h-10 w-full rounded-lg border border-white/15 bg-black/60 px-3 text-xs text-zinc-200"
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
              <label className="text-xs text-zinc-400 mb-1.5 block">Target Snapshot (Newer)</label>
              <select
                value={v2}
                onChange={(e) => setV2(e.target.value)}
                className="h-10 w-full rounded-lg border border-white/15 bg-black/60 px-3 text-xs text-zinc-200"
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
              className="h-10 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-lg shadow-purple-500/20"
            >
              Compare Snapshots
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Diff Output */}
      {loading ? (
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          Computing snapshot diff...
        </div>
      ) : diffResult ? (
        <div className="space-y-4">
          {diffResult.changes?.length === 0 ? (
            <Card className="border-white/10 bg-zinc-950/40 p-8 text-center">
              <Check className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-white">Snapshots are identical</p>
              <p className="text-xs text-zinc-400 mt-1">No differences found between {v1} and {v2}.</p>
            </Card>
          ) : (
            diffResult.changes?.map((ch: any, i: number) => (
              <Card key={i} className="border-white/10 bg-zinc-950/80 overflow-hidden">
                <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 bg-black/40">
                  <div className="flex items-center gap-2 font-mono text-xs text-zinc-200">
                    <FileCode className="h-4 w-4 text-purple-400" />
                    <span>{ch.file}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant="emerald" className="text-[10px] font-mono gap-1">
                      <Plus className="h-3 w-3" />
                      <span>{ch.lines_added || 0}</span>
                    </Badge>
                    <Badge variant="destructive" className="text-[10px] font-mono gap-1">
                      <Minus className="h-3 w-3" />
                      <span>{ch.lines_removed || 0}</span>
                    </Badge>
                  </div>
                </div>

                <ScrollArea className="max-h-96 p-4 font-mono text-xs leading-relaxed bg-black/60">
                  <pre className="text-zinc-300 whitespace-pre-wrap selection:bg-purple-500/30">
                    {ch.diff_text}
                  </pre>
                </ScrollArea>
              </Card>
            ))
          )}
        </div>
      ) : (
        <Card className="border-white/10 bg-zinc-950/40 p-8 text-center">
          <p className="text-xs text-zinc-500">
            Select documentation source and snapshot versions above to compute side-by-side diffs.
          </p>
        </Card>
      )}
    </div>
  )
}
