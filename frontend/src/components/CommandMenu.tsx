import React from "react"
import { 
  CommandDialog, 
  CommandInput, 
  CommandList, 
  CommandEmpty, 
  CommandGroup, 
  CommandItem, 
  CommandShortcut 
} from "@/components/ui/command"
import { 
  Download, 
  Library, 
  Search, 
  GitCompare, 
  FileUp, 
  Activity, 
  FolderOpen,
  Sparkles 
} from "lucide-react"
import { TabId } from "./AppSidebar"
import { pyApi } from "@/lib/bridge"

interface CommandMenuProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelectTab: (tab: TabId) => void
  libraryItems: any[]
  onOpenDocReader: (domain: string) => void
  onOpenAbout?: () => void
}

export const CommandMenu: React.FC<CommandMenuProps> = ({
  open,
  onOpenChange,
  onSelectTab,
  libraryItems,
  onOpenDocReader,
  onOpenAbout
}) => {
  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search documentation..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        
        <CommandGroup heading="Navigation">
          <CommandItem
            onSelect={() => {
              onSelectTab("capture")
              onOpenChange(false)
            }}
          >
            <Download className="mr-2 h-4 w-4 text-cyan-400" />
            <span>Capture Studio</span>
            <CommandShortcut>Tab 1</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => {
              onSelectTab("library")
              onOpenChange(false)
            }}
          >
            <Library className="mr-2 h-4 w-4 text-sky-400" />
            <span>Document Library</span>
            <CommandShortcut>Tab 2</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => {
              onSelectTab("search")
              onOpenChange(false)
            }}
          >
            <Search className="mr-2 h-4 w-4 text-amber-400" />
            <span>Search Studio</span>
            <CommandShortcut>Tab 3</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => {
              onSelectTab("diff")
              onOpenChange(false)
            }}
          >
            <GitCompare className="mr-2 h-4 w-4 text-purple-400" />
            <span>Snapshot Diff</span>
            <CommandShortcut>Tab 4</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => {
              onSelectTab("export")
              onOpenChange(false)
            }}
          >
            <FileUp className="mr-2 h-4 w-4 text-emerald-400" />
            <span>Export Studio (RAG / PDF / JSONL)</span>
            <CommandShortcut>Tab 5</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => {
              onSelectTab("diagnostics")
              onOpenChange(false)
            }}
          >
            <Activity className="mr-2 h-4 w-4 text-rose-400" />
            <span>Diagnostics &amp; System</span>
            <CommandShortcut>Tab 6</CommandShortcut>
          </CommandItem>
        </CommandGroup>

        {libraryItems.length > 0 && (
          <CommandGroup heading="Downloaded Document Sets">
            {libraryItems.map((item) => (
              <CommandItem
                key={item.domain}
                onSelect={() => {
                  onOpenDocReader(item.domain)
                  onOpenChange(false)
                }}
              >
                <Sparkles className="mr-2 h-4 w-4 text-cyan-400" />
                <span className="font-mono text-xs">{item.domain}</span>
                <span className="ml-2 text-xs text-muted-foreground">({item.pages || item.page_count || 0} pages)</span>
                <CommandShortcut>Open Reader</CommandShortcut>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        <CommandGroup heading="Quick Actions">
          <CommandItem
            onSelect={async () => {
              const info = await pyApi.getSystemInfo()
              if (info.library_dir) {
                pyApi.openFolder(info.library_dir)
              }
              onOpenChange(false)
            }}
          >
            <FolderOpen className="mr-2 h-4 w-4 text-yellow-400" />
            <span>Open Library Storage Folder in Explorer</span>
          </CommandItem>

          {onOpenAbout && (
            <CommandItem
              onSelect={() => {
                onOpenAbout()
                onOpenChange(false)
              }}
            >
              <Sparkles className="mr-2 h-4 w-4 text-rose-400" />
              <span>About DocHarvest &amp; Author (Rohan Shetty)</span>
            </CommandItem>
          )}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
