import React, { useState } from "react"
import { Search, Sparkles, BookOpen, ExternalLink, Hash, Copy, Check, Filter } from "lucide-react"
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
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6 animate-in fade-in-50 duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Search className="h-6 w-6 text-primary" />
            <span>Search Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs border border-border bg-muted/60">
            SQLite FTS5 & BM25
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Search across headers, code blocks, and full markdown text with BM25 keyword relevance ranking.
        </p>
      </div>

      {/* Search Input Bar */}
      <Card className="glass-card shadow-sm">
        <CardContent className="p-5 space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Query keyword, function name, API endpoint, or topic..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10 h-11 text-sm bg-background/80 font-mono focus-visible:ring-2 focus-visible:ring-primary/40 rounded-lg"
              />
            </div>

            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="h-11 rounded-lg border border-border bg-background/80 px-3 text-xs text-foreground outline-none focus:ring-2 focus:ring-primary/40 font-mono"
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
              disabled={searching || !query.trim()}
              className="h-11 px-7 font-semibold bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20 interactive-scale"
            >
              {searching ? "Searching..." : "Search"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {searching ? (
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground font-mono">
          Querying full-text search index...
        </div>
      ) : hasSearched && results.length === 0 ? (
        <Card className="glass-card p-10 text-center border-dashed border-border/80">
          <p className="text-sm text-muted-foreground">No matches found for "{query}". Try a different keyword or search across all domains.</p>
        </Card>
      ) : results.length > 0 ? (
        <div className="space-y-3.5 animate-in fade-in-50 duration-300">
          <div className="flex items-center justify-between text-xs text-muted-foreground font-mono px-1">
            <span>Found {results.length} matching section{results.length === 1 ? "" : "s"}</span>
            <span>Ranked by BM25 relevance</span>
          </div>

          <div className="flex flex-col gap-3">
            {results.map((r, idx) => (
              <Card key={idx} className="glass-card p-4.5 hover:border-primary/50 transition-all shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-2 overflow-hidden flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-foreground truncate font-mono">{r.title || r.domain}</span>
                      <Badge variant="outline" className="text-[10px] font-mono py-0 h-4 border-border text-muted-foreground">
                        {r.domain}
                      </Badge>
                      {r.rank !== undefined && (
                        <Badge variant="secondary" className="text-[9px] font-mono py-0 h-4 bg-muted/60 text-muted-foreground">
                          score: {r.rank}
                        </Badge>
                      )}
                    </div>
                    {r.snippet && (
                      <p className="text-xs text-muted-foreground font-mono leading-relaxed line-clamp-3 bg-muted/30 p-2.5 rounded-lg border border-border/40 select-text">
                        {r.snippet}
                      </p>
                    )}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onOpenDocReader(r.domain)}
                    className="h-8 text-xs shrink-0 text-primary border-primary/30 hover:bg-primary/10 interactive-scale"
                  >
                    <BookOpen className="h-3.5 w-3.5 mr-1.5" />
                    Read
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}
