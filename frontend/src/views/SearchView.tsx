import React, { useState } from "react"
import { Search, Sparkles, BookOpen, ExternalLink, Hash } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { pyApi } from "@/lib/bridge"
import { toast } from "sonner"

interface SearchViewProps {
  library: any[]
  onOpenDocReader: (domain: string) => void
}

export const SearchView: React.FC<SearchViewProps> = ({ library, onOpenDocReader }) => {
  const [query, setQuery] = useState<string>("")
  const [selectedDomain, setSelectedDomain] = useState<string>("all")
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState<boolean>(false)
  const [hasSearched, setHasSearched] = useState<boolean>(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setSearching(true)
    setHasSearched(true)
    try {
      const domainFilter = selectedDomain === "all" ? undefined : selectedDomain
      const hits = await pyApi.searchDocs(query.trim(), domainFilter)
      setResults(hits || [])
    } catch (err: any) {
      toast.error(`Search error: ${err.message}`)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="default" className="bg-amber-500/20 text-amber-400 border-amber-500/30">
            SQLite FTS5
          </Badge>
          <span className="text-xs text-zinc-400">Full-Text Indexed Search</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <Search className="h-6 w-6 text-amber-400" />
          <span>Search Studio</span>
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Search across headers, code blocks, and markdown text with BM25 keyword relevance ranking.
        </p>
      </div>

      {/* Search Input Bar */}
      <Card className="border-white/10 bg-zinc-950/70">
        <CardContent className="p-5 space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3 h-4 w-4 text-amber-400" />
              <Input
                placeholder="Query keyword, function name, API endpoint, or topic..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10 h-11 text-sm bg-black/60 font-mono border-white/15"
              />
            </div>

            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="h-11 rounded-lg border border-white/15 bg-black/60 px-3 text-xs text-zinc-200"
            >
              <option value="all">All Documentation Domains</option>
              {library.map((item) => (
                <option key={item.domain} value={item.domain}>
                  {item.domain}
                </option>
              ))}
            </select>

            <Button
              onClick={handleSearch}
              className="h-11 px-6 font-semibold bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white shadow-lg shadow-amber-500/20"
            >
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {searching ? (
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          Querying documentation index...
        </div>
      ) : hasSearched && results.length === 0 ? (
        <Card className="border-white/10 bg-zinc-950/40 p-8 text-center">
          <p className="text-sm text-zinc-400">No matching documentation snippets found for "{query}".</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {results.map((res, i) => (
            <Card key={i} className="border-white/10 bg-zinc-950/60 hover:border-amber-500/30 transition-all p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px] font-mono text-zinc-400 border-white/10">
                      {res.domain}
                    </Badge>
                    <span className="font-semibold text-sm text-white">{res.title || "Section"}</span>
                  </div>
                  <p className="text-xs text-zinc-300 font-mono bg-black/40 p-2.5 rounded-lg border border-white/5 leading-relaxed">
                    {res.snippet}
                  </p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onOpenDocReader(res.domain)}
                  className="h-8 gap-1.5 text-xs text-zinc-300 hover:text-white border-white/15"
                >
                  <BookOpen className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Open</span>
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
