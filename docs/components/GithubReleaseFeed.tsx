'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { GitCommit, Download, Star, GitBranch, ExternalLink, ShieldCheck, Sparkles } from 'lucide-react';
import { GithubIcon, WindowsIcon, LinuxIcon, AppleIcon } from './Icons';
import { DocHarvestGithubData } from '../lib/github';

interface GithubReleaseFeedProps {
  data: DocHarvestGithubData;
}

export function GithubReleaseFeed({ data }: GithubReleaseFeedProps) {
  const { latestRelease, stats, recentCommits } = data;

  return (
    <section id="releases" className="border-b border-border bg-card/20 py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-cyan-400" />
                // 07 / RELEASES &amp; TELEMETRY
              </span>
              <div className="h-px w-24 bg-border/60" />
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
              Latest Release &amp; Live Build Telemetry
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-2xl">
              Standalone binaries, release notes, and real-time commit logs from the active repository pipeline.
            </p>
          </div>

          {/* GitHub Star & Repo Callout */}
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/RohannShetty/gitbook-downloader"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 h-10 px-4 rounded-lg border border-border bg-card hover:bg-secondary font-mono text-xs font-bold text-foreground transition-all shadow-sm"
            >
              <GithubIcon className="h-4 w-4" />
              <span>RohannShetty/gitbook-downloader</span>
              <span className="ml-1 px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 text-[10px]">
                ★ {stats.stars}
              </span>
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Downloadable Binaries & Release Notes */}
          <div className="lg:col-span-6 space-y-6">
            <div className="border border-border rounded-xl bg-card p-6 sm:p-7 shadow-xl space-y-6">
              
              {/* Release Header */}
              <div className="flex items-center justify-between border-b border-border/80 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                      {latestRelease.tag}
                    </span>
                    <span className="font-mono text-[10px] text-muted-foreground">
                      Published: {latestRelease.publishedAt}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-foreground">
                    {latestRelease.name}
                  </h3>
                </div>

                <a
                  href={latestRelease.htmlUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 rounded-lg border border-border bg-background text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors"
                  title="View on GitHub"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>

              {/* Release Body Summary */}
              <p className="text-xs text-muted-foreground font-mono leading-relaxed">
                {latestRelease.body}
              </p>

              {/* Binary Download Buttons */}
              <div className="space-y-3">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block">
                  Official Cross-Platform Binaries:
                </span>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {/* Windows */}
                  <a
                    href="https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.0/docharvest-windows-latest.exe"
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-secondary/50 hover:border-primary hover:bg-primary/10 transition-all text-center group cursor-pointer"
                  >
                    <WindowsIcon className="h-5 w-5 text-indigo-400 group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">Windows</span>
                    <span className="font-mono text-[9px] text-muted-foreground">docharvest.exe (32.9MB)</span>
                  </a>

                  {/* Linux */}
                  <a
                    href="https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.0/docharvest-linux-x86_64"
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-secondary/50 hover:border-primary hover:bg-primary/10 transition-all text-center group cursor-pointer"
                  >
                    <LinuxIcon className="h-5 w-5 text-amber-400 group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">Linux</span>
                    <span className="font-mono text-[9px] text-muted-foreground">x86_64 Binary (28.4MB)</span>
                  </a>

                  {/* macOS */}
                  <a
                    href="https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.0/docharvest-macos-universal"
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-secondary/50 hover:border-primary hover:bg-primary/10 transition-all text-center group cursor-pointer"
                  >
                    <AppleIcon className="h-5 w-5 text-cyan-400 group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">macOS</span>
                    <span className="font-mono text-[9px] text-muted-foreground">Universal Binary (31.2MB)</span>
                  </a>
                </div>
              </div>

              {/* SHA256 Verification Badge */}
              <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground border-t border-border/60 pt-4">
                <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>All releases signed and verified with SHA-256 checksums in GitHub CI.</span>
              </div>

            </div>
          </div>

          {/* Right Column: Live Commit Log Stream */}
          <div className="lg:col-span-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-2 font-mono text-xs">
              <span className="font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                <GitCommit className="h-4 w-4 text-cyan-400 animate-pulse" />
                <span>Recent Commit Stream (master)</span>
              </span>
              <span className="text-muted-foreground text-[10px]">LIVE PIPELINE</span>
            </div>

            <div className="border border-border rounded-xl bg-card divide-y divide-border/60 max-h-[460px] overflow-y-auto">
              {recentCommits.map((commit, index) => (
                <a
                  key={commit.sha + index}
                  href={commit.url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-4 flex gap-3 text-xs font-mono group hover:bg-secondary/40 transition-colors block"
                >
                  <div className="text-cyan-400 pt-0.5 select-none font-bold">
                    [{commit.sha}]
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="text-foreground leading-snug group-hover:text-primary transition-colors">
                      {commit.message}
                    </p>
                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                      <span className="text-foreground">{commit.author}</span>
                      <span>•</span>
                      <span>{commit.date}</span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
