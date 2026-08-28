'use client';

import React from 'react';
import Link from 'next/link';
import { Terminal, Heart, ArrowUp, Mail } from 'lucide-react';
import { GithubIcon, LinkedinIcon, XIcon } from './Icons';

export function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="border-t border-border bg-card/50 py-16 text-muted-foreground font-mono text-xs transition-colors duration-200">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 pb-12 border-b border-border/80">
          
          {/* Col 1: Brand & Attribution */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-mono font-bold text-base shadow-sm">
                <Terminal className="h-4 w-4 text-white" />
              </div>
              <span className="font-mono text-base font-extrabold tracking-tight text-foreground">
                DocHarvest
              </span>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-muted/60 text-muted-foreground border border-border/50">
                v11.0.1
              </span>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed max-w-sm">
              Universal documentation harvester, RAG vector dataset compiler, and publication-grade offline PDF generator for AI agents.
            </p>

            {/* Creator Attribution Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card text-foreground font-semibold shadow-xs">
              <span>Made with</span>
              <Heart className="h-3.5 w-3.5 text-rose-500 fill-rose-500" />
              <span>by</span>
              <a
                href="https://github.com/RohannShetty"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline font-bold"
              >
                Rohan Shetty
              </a>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <span className="font-bold text-foreground block uppercase text-[11px] tracking-wider">
              Navigation
            </span>
            <ul className="space-y-2 text-muted-foreground font-sans text-xs">
              <li>
                <a href="#agents" className="hover:text-primary transition-colors text-cyan-700 dark:text-cyan-400 font-semibold">Agents &amp; IDEs</a>
              </li>
              <li>
                <a href="#platforms" className="hover:text-foreground transition-colors">Platforms</a>
              </li>
              <li>
                <a href="#contract" className="hover:text-foreground transition-colors">Output Contract</a>
              </li>
              <li>
                <a href="#studio" className="hover:text-foreground transition-colors">Export Studio</a>
              </li>
              <li>
                <a href="#matrix" className="hover:text-foreground transition-colors">Capability Matrix</a>
              </li>
              <li>
                <a href="#mcp" className="hover:text-foreground transition-colors">FastMCP Server</a>
              </li>
              <li>
                <a href="#releases" className="hover:text-foreground transition-colors">Live Releases</a>
              </li>
            </ul>
          </div>

          {/* Col 3: Community & Social Links */}
          <div className="md:col-span-4 space-y-3">
            <span className="font-bold text-foreground block uppercase text-[11px] tracking-wider">
              Community &amp; Connect
            </span>
            
            <div className="flex gap-2">
              <a
                href="https://github.com/RohannShetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="GitHub Profile"
              >
                <GithubIcon className="h-4 w-4" />
              </a>
              <a
                href="https://www.linkedin.com/in/rohan-shettyy/"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="LinkedIn Profile"
              >
                <LinkedinIcon className="h-4 w-4" />
              </a>
              <a
                href="https://x.com/rohan__shetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="X / Twitter"
              >
                <XIcon className="h-4 w-4" />
              </a>
              <a
                href="mailto:shettyrohan2@gmail.com"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="Email Rohan Shetty"
              >
                <Mail className="h-4 w-4" />
              </a>
            </div>

            <p className="text-[11px] text-muted-foreground leading-normal pt-1">
              DocHarvest is open-source under the MIT License. Contributions and PRs are always welcome.
            </p>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-8 text-[11px] text-muted-foreground">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            <span>&copy; {new Date().getFullYear()} DocHarvest (GitBook Downloader). MIT Licensed.</span>
            <span className="hidden sm:inline">•</span>
            <span>Created by Rohan Shetty</span>
          </div>

          <button
            onClick={scrollToTop}
            className="inline-flex items-center gap-1.5 hover:text-foreground text-left cursor-pointer transition-colors border border-border bg-card px-3 py-1.5 rounded-lg"
          >
            <span>Back to top</span>
            <ArrowUp className="h-3 w-3" />
          </button>
        </div>

      </div>
    </footer>
  );
}
