import React, { useState, useEffect } from "react"
import { AppSidebar, TabId } from "@/components/AppSidebar"
import { CommandMenu } from "@/components/CommandMenu"
import { DocReaderModal } from "@/components/DocReaderModal"
import { CaptureStudio } from "@/views/CaptureStudio"
import { LibraryView } from "@/views/LibraryView"
import { SearchView } from "@/views/SearchView"
import { DiffView } from "@/views/DiffView"
import { ExportView } from "@/views/ExportView"
import { DiagnosticsView } from "@/views/DiagnosticsView"
import { Toaster } from "@/components/ui/sonner"
import { pyApi } from "@/lib/bridge"

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>("capture")
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false)
  const [theme, setTheme] = useState<"dark" | "light">("dark")
  const [cmdMenuOpen, setCmdMenuOpen] = useState<boolean>(false)
  
  // Library State
  const [library, setLibrary] = useState<any[]>([])
  const [loadingLibrary, setLoadingLibrary] = useState<boolean>(false)
  
  // Modal State
  const [readerDomain, setReaderDomain] = useState<string | null>(null)
  const [exportDomain, setExportDomain] = useState<string | undefined>(undefined)

  const loadLibrary = async () => {
    setLoadingLibrary(true)
    try {
      const items = await pyApi.listLibrary()
      setLibrary(items || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingLibrary(false)
    }
  }

  // Reload library on mount and whenever the active tab changes to keep UI synchronized
  useEffect(() => {
    loadLibrary()
  }, [activeTab])

  // Set default theme class on document element
  useEffect(() => {
    document.documentElement.classList.add("dark")
  }, [])


  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setCmdMenuOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  // Theme switcher
  const handleToggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark"
    setTheme(next)
    if (next === "dark") {
      document.documentElement.classList.add("dark")
      document.documentElement.classList.remove("light")
    } else {
      document.documentElement.classList.add("light")
      document.documentElement.classList.remove("dark")
    }
  }

  const handleSelectExport = (domain: string) => {
    setExportDomain(domain)
    setActiveTab("export")
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background font-sans text-foreground">
      {/* Collapsible Modern Sidebar */}
      <AppSidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        libraryCount={library.length}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col overflow-y-auto relative bg-background/50">
        {activeTab === "capture" && (
          <CaptureStudio
            onCaptureCompleted={loadLibrary}
            onOpenDocReader={setReaderDomain}
          />
        )}
        {activeTab === "library" && (
          <LibraryView
            library={library}
            loading={loadingLibrary}
            onRefresh={loadLibrary}
            onOpenDocReader={setReaderDomain}
            onSelectExport={handleSelectExport}
          />
        )}
        {activeTab === "search" && (
          <SearchView
            library={library}
            onOpenDocReader={setReaderDomain}
          />
        )}
        {activeTab === "diff" && (
          <DiffView library={library} />
        )}
        {activeTab === "export" && (
          <ExportView library={library} selectedDomain={exportDomain} />
        )}
        {activeTab === "diagnostics" && (
          <DiagnosticsView />
        )}
      </main>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandMenu
        open={cmdMenuOpen}
        onOpenChange={setCmdMenuOpen}
        onSelectTab={setActiveTab}
        libraryItems={library}
        onOpenDocReader={setReaderDomain}
      />

      {/* Split-View Markdown Reader Modal */}
      <DocReaderModal
        domain={readerDomain}
        onClose={() => setReaderDomain(null)}
      />

      {/* Toast Notification Container */}
      <Toaster theme={theme} />
    </div>
  )
}
export default App
