'use client';

import React from 'react';
import Link from 'next/link';
import { Terminal, Heart, ArrowUp, Mail } from 'lucide-react';
import { GithubIcon, LinkedinIcon } from './Icons';

export function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="border-t border-border bg-[#07070a] py-16 text-zinc-400 font-mono text-xs">
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
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-bold">
                v10.0.1
              </span>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed max-w-sm">
              Universal documentation harvester, RAG vector dataset compiler, and publication-grade offline PDF generator for AI agents.
            </p>

            {/* Creator Attribution Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card/80 text-foreground font-semibold">
              <span>Made with</span>
              <Heart className="h-3.5 w-3.5 text-rose-500 fill-rose-500" />
              <span>by</span>
              <a
                href="https://github.com/RohannShetty"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline"
              >
                Rohan Shetty
              </a>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <span className="font-bold text-foreground block uppercase text-[11px] tracking-wider">
              // Navigation
            </span>
            <ul className="space-y-2 text-muted-foreground">
              <li>
                <a href="#platforms" className="hover:text-foreground transition-colors">// platforms</a>
              </li>
              <li>
                <a href="#contract" className="hover:text-foreground transition-colors">// output-contract</a>
              </li>
              <li>
                <a href="#studio" className="hover:text-foreground transition-colors">// export-studio</a>
              </li>
              <li>
                <a href="#matrix" className="hover:text-foreground transition-colors">// capability-matrix</a>
              </li>
              <li>
                <a href="#mcp" className="hover:text-foreground transition-colors">// fastmcp-server</a>
              </li>
              <li>
                <a href="#releases" className="hover:text-foreground transition-colors">// live-releases</a>
              </li>
            </ul>
          </div>

          {/* Col 3: Community & Social Links */}
          <div className="md:col-span-4 space-y-3">
            <span className="font-bold text-foreground block uppercase text-[11px] tracking-wider">
              // Community &amp; Connect
            </span>
            
            <div className="flex gap-2">
              <a
                href="https://github.com/RohannShetty/gitbook-downloader"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="GitHub Repository"
              >
                <GithubIcon className="h-4 w-4" />
              </a>
              <a
                href="https://linkedin.com/in/rohannshetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                title="LinkedIn"
              >
                <LinkedinIcon className="h-4 w-4" />
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
