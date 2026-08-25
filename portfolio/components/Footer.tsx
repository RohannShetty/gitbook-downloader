'use client';

import React from 'react';
import Link from 'next/link';
import { Mail, ArrowUp } from 'lucide-react';
import { GithubIcon, LinkedinIcon, TwitterIcon } from './Icons';

export default function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="border-t border-border bg-card/25 py-12 relative overflow-hidden">
      {/* Structural layout lines */}
      <div className="absolute top-0 bottom-0 left-[8%] border-l border-border/40 pointer-events-none hidden lg:block" />
      <div className="absolute top-0 bottom-0 right-[8%] border-r border-border/40 pointer-events-none hidden lg:block" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 pb-8 border-b border-border/80">
          
          {/* Logo & Direct Contact Call (Left Columns) */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-mono font-bold text-base shadow-sm">
                R
              </div>
              <span className="font-mono text-sm font-bold tracking-tight text-foreground">
                Rohan Shetty
              </span>
            </div>
            <p className="text-xs text-muted-foreground font-mono leading-relaxed max-w-sm">
              Developing high-end structural computational systems, quantitative algorithms, and local AI agent integrations.
            </p>
            <div className="pt-2">
              <a
                href="mailto:shettyrohan2@gmail.com"
                className="inline-flex h-9 items-center justify-center rounded-lg border border-border bg-background px-4 text-xs font-mono font-bold text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all duration-200"
              >
                Get in touch
              </a>
            </div>
          </div>

          {/* Sitemap (Middle Columns) */}
          <div className="md:col-span-3 space-y-3 font-mono text-xs">
            <span className="font-bold text-foreground block">
              // Navigation
            </span>
            <ul className="space-y-2 text-muted-foreground">
              <li>
                <Link href="/#about" className="hover:text-foreground transition-colors">// about</Link>
              </li>
              <li>
                <Link href="/#projects" className="hover:text-foreground transition-colors">// projects</Link>
              </li>
              <li>
                <Link href="/#skills" className="hover:text-foreground transition-colors">// skills</Link>
              </li>
              <li>
                <Link href="/#blog" className="hover:text-foreground transition-colors">// blog</Link>
              </li>
            </ul>
          </div>

          {/* Social Channels (Right Columns) */}
          <div className="md:col-span-4 space-y-3 font-mono text-xs">
            <span className="font-bold text-foreground block">
              // Channels
            </span>
            <div className="flex gap-2">
              <a
                href="https://github.com/rohannshetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-background hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-200"
                title="GitHub"
              >
                <GithubIcon className="h-4 w-4" />
              </a>
              <a
                href="https://linkedin.com/in/rohannshetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-background hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-200"
                title="LinkedIn"
              >
                <LinkedinIcon className="h-4 w-4" />
              </a>
              <a
                href="https://twitter.com/rohannshetty"
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-border bg-background hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-200"
                title="Twitter"
              >
                <TwitterIcon className="h-4 w-4" />
              </a>
            </div>
            <p className="text-[10px] text-muted-foreground leading-normal pt-1">
              Active across open-source communities. Feel free to reach out for collaboration.
            </p>
          </div>

        </div>

        {/* Bottom Credits & Up Trigger */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6 text-[10px] font-mono text-muted-foreground">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            <span>&copy; {new Date().getFullYear()} Rohan Shetty. All rights reserved.</span>
            <span className="hidden sm:inline">•</span>
            <span>Built with Next.js 16, Tailwind CSS v4, Vercel.</span>
          </div>

          <button
            onClick={scrollToTop}
            className="flex items-center gap-1.5 hover:text-foreground text-left cursor-pointer transition-colors border border-border bg-background/50 hover:bg-secondary px-2.5 py-1 rounded-md"
          >
            <span>Scroll to Top</span>
            <ArrowUp className="h-3 w-3" />
          </button>
        </div>

      </div>
    </footer>
  );
}
