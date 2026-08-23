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
  TerminalSquare
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
  libraryCount: number
}

export const AppSidebar: React.FC<AppSidebarProps> = ({
  activeTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  theme,
  onToggleTheme,
  libraryCount
}) => {
  const navItems = [
    { id: "capture" as TabId, label: "Capture Studio", icon: Download, badge: null },
    { id: "library" as TabId, label: "Document Library", icon: Library, badge: libraryCount > 0 ? `${libraryCount}` : null },
    { id: "search" as TabId, label: "Search Studio", icon: Search, badge: null },
    { id: "diff" as TabId, label: "Snapshot Diff", icon: GitCompare, badge: null },
    { id: "export" as TabId, label: "Export Studio", icon: FileUp, badge: "RAG" },
    { id: "diagnostics" as TabId, label: "Diagnostics", icon: Activity, badge: null },
  ]

  return (
    <aside
      className={`relative flex flex-col border-r border-white/10 bg-zinc-950/80 backdrop-blur-xl transition-all duration-300 select-none ${
        isCollapsed ? "w-18" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-white/10 px-4">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-500 to-cyan-400 shadow-md shadow-cyan-500/20 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-bold tracking-tight text-white text-sm">GitBook DL</span>
                <Badge variant="default" className="text-[10px] px-1.5 py-0 h-4 bg-cyan-500/20 text-cyan-400 border-cyan-500/40 font-mono">
                  v9.0
                </Badge>
              </div>
              <span className="text-[11px] text-muted-foreground font-medium truncate">Pro Doc Engine</span>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="flex h-9 w-9 mx-auto items-center justify-center rounded-xl bg-gradient-to-tr from-sky-500 to-cyan-400 shadow-md shadow-cyan-500/20 text-white">
            <Sparkles className="h-5 w-5" />
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1.5 p-3">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              title={isCollapsed ? item.label : undefined}
              className={`group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "bg-gradient-to-r from-sky-500/15 to-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm"
                  : "text-zinc-400 hover:bg-white/5 hover:text-zinc-100"
              }`}
            >
              <Icon
                className={`h-4 w-4 shrink-0 transition-transform group-hover:scale-110 ${
                  isActive ? "text-cyan-400" : "text-zinc-400"
                }`}
              />
              {!isCollapsed && (
                <div className="flex flex-1 items-center justify-between overflow-hidden">
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <Badge
                      variant="outline"
                      className="ml-auto text-[10px] h-4.5 px-1.5 border-white/10 text-zinc-400 bg-white/5"
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
      <div className="border-t border-white/10 p-3 space-y-2">
        <div className={`flex items-center ${isCollapsed ? "flex-col" : "justify-between"}`}>
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleTheme}
            className="h-8 w-8 text-zinc-400 hover:text-zinc-100"
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleCollapse}
            className="h-8 w-8 text-zinc-400 hover:text-zinc-100"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {!isCollapsed && (
          <div className="rounded-lg bg-white/5 p-2 text-center text-[11px] text-zinc-500 flex items-center justify-center gap-1">
            <TerminalSquare className="h-3 w-3 text-cyan-400" />
            <span>Press <kbd className="px-1 py-0.5 rounded bg-black/40 border border-white/10 font-mono text-[10px] text-zinc-300">Ctrl+K</kbd> for Menu</span>
          </div>
        )}
      </div>
    </aside>
  )
}
