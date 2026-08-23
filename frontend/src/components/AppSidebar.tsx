import React from "react"
import { 
  Download, 
  Library, 
  Search, 
  GitCompare, 
  FileUp, 
  Activity, 
  ChevronLeft, 
  ChevronRight, 
  Sparkles, 
  Sun, 
  Moon,
  Command,
  Heart,
  Info
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export type TabId = "capture" | "library" | "search" | "diff" | "export" | "diagnostics"

interface AppSidebarProps {
  activeTab: TabId
  onSelectTab: (tab: TabId) => void
  isCollapsed: boolean
  onToggleCollapse: () => void
  theme: "dark" | "light"
  onToggleTheme: () => void
  libraryCount?: number
  onOpenAbout?: () => void
}

export const AppSidebar: React.FC<AppSidebarProps> = ({
  activeTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  theme,
  onToggleTheme,
  onOpenAbout
}) => {
  const navItems = [
    { id: "capture" as TabId, label: "Capture Studio", icon: Download, badge: null },
    { id: "library" as TabId, label: "Document Library", icon: Library, badge: null },
    { id: "search" as TabId, label: "Search Studio", icon: Search, badge: null },
    { id: "diff" as TabId, label: "Snapshot Diff", icon: GitCompare, badge: null },
    { id: "export" as TabId, label: "Export Studio", icon: FileUp, badge: "RAG" },
    { id: "diagnostics" as TabId, label: "Diagnostics", icon: Activity, badge: null },
  ]

  return (
    <aside
      className={`relative flex flex-col border-r border-border bg-card/90 backdrop-blur-xl transition-all duration-300 select-none ${
        isCollapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-border px-3.5">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-bold tracking-tight text-foreground text-sm font-mono">DocHarvest</span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 border-cyan-500/30 text-cyan-400 bg-cyan-500/10 font-mono">
                  v10.0.1
                </Badge>
              </div>
              <span className="text-[11px] text-muted-foreground font-medium truncate">Universal Doc Harvester</span>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="flex h-8 w-8 mx-auto items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              title={isCollapsed ? item.label : undefined}
              className={`group flex w-full items-center gap-3 rounded-md px-2.5 py-2 text-xs font-medium transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary font-semibold border border-primary/20 shadow-xs"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <Icon
                className={`h-4 w-4 shrink-0 transition-transform group-hover:scale-105 ${
                  isActive ? "text-primary" : "text-muted-foreground"
                }`}
              />
              {!isCollapsed && (
                <div className="flex flex-1 items-center justify-between overflow-hidden">
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <Badge
                      variant="secondary"
                      className="ml-auto text-[10px] h-4 px-1.5 font-normal"
                    >
                      {item.badge}
                    </Badge>
                  )}
                </div>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer Controls */}
      <div className="border-t border-border p-2.5 space-y-2">
        <div className={`flex items-center ${isCollapsed ? "flex-col gap-1.5" : "justify-between"}`}>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleTheme}
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {onOpenAbout && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onOpenAbout}
                className="h-8 w-8 text-muted-foreground hover:text-cyan-400"
                title="About DocHarvest & Author"
              >
                <Heart className="h-3.5 w-3.5 text-rose-500/80 hover:text-rose-500" />
              </Button>
            )}
          </div>

          {!isCollapsed && (
            <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <kbd className="px-1.5 py-0.5 rounded border border-border bg-muted text-[10px] font-mono flex items-center gap-0.5">
                <Command className="h-2.5 w-2.5" /> K
              </kbd>
            </div>
          )}

          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleCollapse}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </aside>
  )
}
