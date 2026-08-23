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
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
            <Search className="h-6 w-6 text-primary" />
            <span>Search Studio</span>
          </h1>
          <Badge variant="secondary" className="font-mono text-xs">
            SQLite FTS5
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Search across headers, code blocks, and markdown text with BM25 keyword relevance ranking.
        </p>
      </div>

      {/* Search Input Bar */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
        <CardContent className="p-5 space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Query keyword, function name, API endpoint, or topic..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10 h-11 text-sm bg-background font-mono"
              />
            </div>

            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="h-11 rounded-md border border-border bg-background px-3 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary"
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
              className="h-11 px-6 font-medium bg-primary text-primary-foreground shadow-xs"
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
        <Card className="border-border/60 bg-card/40 p-8 text-center">
          <p className="text-sm text-muted-foreground">No matches found for "{query}".</p>
        </Card>
      ) : results.length > 0 ? (
        <div className="space-y-3">
          <div className="text-xs text-muted-foreground font-mono">
            Found {results.length} result{results.length === 1 ? "" : "s"}
          </div>

          <div className="flex flex-col gap-3">
            {results.map((r, idx) => (
              <Card key={idx} className="border-border/60 bg-card/60 backdrop-blur-sm p-4 hover:border-primary/40 transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1.5 overflow-hidden">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-foreground truncate">{r.title || r.domain}</span>
                      <Badge variant="outline" className="text-[10px] font-mono py-0 h-4 border-border text-muted-foreground">
                        {r.domain}
                      </Badge>
                    </div>
                    {r.snippet && (
                      <p className="text-xs text-muted-foreground font-mono leading-relaxed line-clamp-3 bg-muted/40 p-2 rounded">
                        {r.snippet}
                      </p>
                    )}
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onOpenDocReader(r.domain)}
                    className="h-8 text-xs shrink-0 text-primary hover:text-primary"
                  >
                    <BookOpen className="h-3.5 w-3.5 mr-1" />
                    Open
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
