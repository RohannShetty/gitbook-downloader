'use client';

import React from 'react';
import Link from 'next/link';
import { useTheme } from './ThemeProvider';
import { Sun, Moon, Terminal, Download, Star, Sparkles } from 'lucide-react';
import { GithubIcon } from './Icons';

interface HeaderProps {
  stars?: number;
  onOpenInstallModal: () => void;
}

export function Header({ stars = 128, onOpenInstallModal }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Brand identity */}
        <Link href="/" className="group flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground font-mono font-bold text-lg shadow-md group-hover:scale-105 transition-transform duration-200">
            <Terminal className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-mono text-base font-extrabold tracking-tight text-foreground">
                DocHarvest
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-mono text-cyan-400">
                v11.0.1
              </span>
            </div>
            <span className="text-[10px] text-muted-foreground font-mono tracking-wider">
              Universal Doc Harvester &amp; RAG Compiler
            </span>
          </div>
        </Link>

        {/* Navigation Anchors */}
        <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-muted-foreground">
          <a href="#agents" className="hover:text-foreground transition-colors text-cyan-400">
            Agents &amp; IDEs
          </a>
          <a href="#platforms" className="hover:text-foreground transition-colors">
            Platforms
          </a>
          <a href="#contract" className="hover:text-foreground transition-colors">
            Output Contract
          </a>
          <a href="#studio" className="hover:text-foreground transition-colors">
            Export Studio
          </a>
          <a href="#matrix" className="hover:text-foreground transition-colors">
            Comparison
          </a>
          <a href="#mcp" className="hover:text-foreground transition-colors">
            FastMCP Server
          </a>
          <a href="#releases" className="hover:text-foreground transition-colors">
            Releases
          </a>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          {/* GitHub Star Button */}
          <a
            href="https://github.com/RohannShetty/gitbook-downloader"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 h-9 px-3 rounded-lg border border-border bg-secondary/50 text-xs font-mono text-muted-foreground hover:text-foreground hover:border-primary/40 transition-all duration-200"
          >
            <GithubIcon className="h-4 w-4" />
            <span className="font-bold">Star</span>
            <span className="ml-1 px-1.5 py-0.2 rounded bg-background/80 border border-border text-[10px] font-bold text-foreground">
              {stars}
            </span>
          </a>

          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg border border-border bg-secondary/50 text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all duration-200 cursor-pointer"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <Sun className="h-4 w-4 text-amber-500" />
            ) : (
              <Moon className="h-4 w-4 text-indigo-500" />
            )}
          </button>

          {/* Quick Install Trigger CTA */}
          <button
            onClick={onOpenInstallModal}
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-lg bg-primary px-4 text-xs font-mono font-bold text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20 transition-all duration-200 cursor-pointer active:scale-95"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Install CLI / GUI</span>
          </button>
        </div>

      </div>
    </header>
  );
}
