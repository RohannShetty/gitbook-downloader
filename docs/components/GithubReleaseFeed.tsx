'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  GitCommit, 
  Download, 
  Star, 
  GitBranch, 
  ExternalLink, 
  ShieldCheck, 
  Sparkles, 
  Check, 
  Copy, 
  Terminal, 
  Clock, 
  Tag, 
  Zap, 
  ArrowUpRight,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { GithubIcon, WindowsIcon, LinuxIcon, AppleIcon } from './Icons';
import { DocHarvestGithubData, ReleaseInfo, CommitInfo } from '../lib/github';

interface GithubReleaseFeedProps {
  data: DocHarvestGithubData;
}

export function GithubReleaseFeed({ data }: GithubReleaseFeedProps) {
  const [release, setRelease] = useState<ReleaseInfo>(data.latestRelease);
  const [commits, setCommits] = useState<CommitInfo[]>(data.recentCommits);
  const [stars, setStars] = useState<number>(data.stats.stars);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copiedSha, setCopiedSha] = useState<string | null>(null);
  const [copiedVerify, setCopiedVerify] = useState<boolean>(false);

  // Client-side live sync
  useEffect(() => {
    let isMounted = true;

    async function fetchLiveGithubData() {
      setIsLoading(true);
      try {
        // 1. Fetch latest release
        const relRes = await fetch('https://api.github.com/repos/RohannShetty/gitbook-downloader/releases/latest');
        if (relRes.ok) {
          const rel = await relRes.json();
          if (isMounted && rel.tag_name) {
            setRelease({
              tag: rel.tag_name,
              name: rel.name || rel.tag_name,
              publishedAt: rel.published_at ? new Date(rel.published_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : 'Today',
              body: rel.body || '',
              htmlUrl: rel.html_url,
              assets: (rel.assets || []).map((a: any) => ({
                name: a.name,
                size: a.size,
                downloadCount: a.download_count,
                browserDownloadUrl: a.browser_download_url,
                os: a.name.includes('.exe') ? 'windows' : a.name.includes('linux') || a.name.includes('ubuntu') ? 'linux' : a.name.includes('macos') ? 'macos' : 'source'
              }))
            });
          }
        }

        // 2. Fetch recent commits
        const commitRes = await fetch('https://api.github.com/repos/RohannShetty/gitbook-downloader/commits?per_page=8');
        if (commitRes.ok) {
          const commData = await commitRes.json();
          if (isMounted && Array.isArray(commData)) {
            setCommits(commData.map((c: any) => ({
              sha: c.sha.substring(0, 7),
              message: c.commit.message.split('\n')[0],
              date: c.commit.author?.date ? new Date(c.commit.author.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Recent',
              author: c.commit.author?.name || 'Rohan Shetty',
              url: c.html_url
            })));
          }
        }

        // 3. Fetch repo stats
        const repoRes = await fetch('https://api.github.com/repos/RohannShetty/gitbook-downloader');
        if (repoRes.ok) {
          const repo = await repoRes.json();
          if (isMounted && repo.stargazers_count !== undefined) {
            setStars(repo.stargazers_count);
          }
        }
      } catch {
        // Graceful fallback to server-rendered props
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    fetchLiveGithubData();
    return () => { isMounted = false; };
  }, []);

  const handleCopySha = (sha: string) => {
    navigator.clipboard.writeText(sha);
    setCopiedSha(sha);
    setTimeout(() => setCopiedSha(null), 2000);
  };

  const handleCopyVerify = () => {
    const cmd = "Get-FileHash -Algorithm SHA256 docharvest-windows-latest.exe";
    navigator.clipboard.writeText(cmd);
    setCopiedVerify(true);
    setTimeout(() => setCopiedVerify(false), 2000);
  };

  // Helper to parse release body into clean structured sections
  const formatReleaseBody = (rawBody: string) => {
    if (!rawBody) return null;

    const lines = rawBody.split('\n');
    const sections: { title?: string; items: string[] }[] = [];
    let currentSection: { title?: string; items: string[] } = { items: [] };

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('# DocHarvest') || trimmed.startsWith('| Asset') || trimmed.startsWith('| :---') || trimmed.startsWith('```')) {
        continue;
      }

      if (trimmed.startsWith('###') || trimmed.startsWith('##')) {
        if (currentSection.items.length > 0 || currentSection.title) {
          sections.push(currentSection);
        }
        currentSection = {
          title: trimmed.replace(/^#+\s*/, '').replace(/[\u{1F300}-\u{1F9FF}]/gu, '').trim(),
          items: []
        };
      } else if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
        const itemText = trimmed.replace(/^[-*]\s*/, '').trim();
        if (itemText && !itemText.startsWith('Full Changelog')) {
          currentSection.items.push(itemText);
        }
      }
    }

    if (currentSection.items.length > 0 || currentSection.title) {
      sections.push(currentSection);
    }

    return sections;
  };

  const parsedSections = formatReleaseBody(release.body);

  return (
    <section id="releases" className="border-b border-border bg-card/30 dark:bg-card/15 py-20 scroll-mt-16 transition-colors duration-200">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-cyan" />
                <span>Releases &amp; Telemetry</span>
              </span>
              <div className="h-px w-24 bg-border-border/80" />
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
              Latest Release &amp; Live Build Telemetry
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-2xl">
              Standalone native binaries, categorized release notes, and live pipeline commits.
            </p>
          </div>

          {/* GitHub Star & Repo Callout */}
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/RohannShetty/gitbook-downloader"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 h-10 px-4 rounded-lg border border-border bg-card hover:bg-secondary/70 font-mono text-xs font-bold text-foreground transition-all shadow-sm group"
            >
              <GithubIcon className="h-4 w-4 group-hover:scale-110 transition-transform" />
              <span>RohannShetty/gitbook-downloader</span>
              <span className="ml-1 px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 text-[10px]">
                ★ {stars}
              </span>
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Formatted Release Card & Binaries */}
          <div className="lg:col-span-7 space-y-6">
            <div className="border border-border rounded-xl bg-card p-6 sm:p-7 shadow-lg shadow-black/5 dark:shadow-2xl dark:shadow-black/40 space-y-6">
              
              {/* Release Header Banner */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border pb-4 gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-card/50 text-cyan border border-border/50">
                      <Tag className="h-3 w-3" />
                      {release.tag}
                    </span>
                    <span className="flex items-center gap-1 font-mono text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {release.publishedAt}
                    </span>
                    {isLoading && (
                      <span className="inline-flex items-center gap-1 font-mono text-[10px] text-primary animate-pulse">
                        <RefreshCw className="h-2.5 w-2.5 animate-spin" />
                        Live
                      </span>
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-foreground tracking-tight">
                    {release.name}
                  </h3>
                </div>

                <a
                  href={release.htmlUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-secondary text-xs font-mono font-medium text-foreground hover:border-primary hover:text-primary transition-colors shadow-xs self-start sm:self-center"
                  title="Inspect on GitHub Releases"
                >
                  <span>GitHub Release</span>
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </a>
              </div>

              {/* Formatted Release Highlights */}
              <div className="space-y-4 font-mono text-xs">
                {parsedSections && parsedSections.length > 0 ? (
                  parsedSections.map((sec, idx) => (
                    <div key={idx} className="space-y-2 rounded-lg bg-muted/40 p-3.5 border border-border/60">
                      {sec.title && (
                        <h4 className="font-bold text-foreground text-xs flex items-center gap-2">
                          <Zap className="h-3.5 w-3.5 text-accent" />
                          <span>{sec.title}</span>
                        </h4>
                      )}
                      <ul className="space-y-1.5 text-muted-foreground pl-1">
                        {sec.items.map((item, iIdx) => {
                          const cleanItem = item.replace(/\*\*(.*?)\*\*/g, '$1');
                          const isHeading = item.startsWith('**');
                          return (
                            <li key={iIdx} className="flex items-start gap-2 leading-relaxed">
                              <span className="text-cyan font-bold mt-0.5">•</span>
                              <span className={isHeading ? "text-foreground font-semibold" : "text-foreground/90"}>
                                {cleanItem}
                              </span>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground leading-relaxed">
                    {release.body || "Fast standalone documentation compiler with FastMCP v2 protocol support."}
                  </p>
                )}
              </div>

              {/* Official Download Binaries Grid */}
              <div className="space-y-3 pt-2">
                <span className="font-mono text-[11px] text-muted-foreground font-semibold uppercase tracking-wider block">
                  Official Cross-Platform Standalone Binaries:
                </span>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {/* Windows */}
                  <a
                    href={`https://github.com/RohannShetty/gitbook-downloader/releases/download/${release.tag}/docharvest-windows-latest.exe`}
                    className="flex flex-col items-center justify-center p-3.5 rounded-lg border border-border bg-secondary/60 hover:border-primary/50 hover:bg-primary/5 transition-all text-center group cursor-pointer focus-visible:outline-2 focus-visible:outline-primary shadow-xs"
                  >
                    <WindowsIcon className="h-5 w-5 text-primary group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">Windows x64</span>
                    <span className="font-mono text-[10px] text-muted-foreground mt-0.5">docharvest.exe (34.5MB)</span>
                  </a>

                  {/* Linux */}
                  <a
                    href={`https://github.com/RohannShetty/gitbook-downloader/releases/download/${release.tag}/docharvest-ubuntu-latest`}
                    className="flex flex-col items-center justify-center p-3.5 rounded-lg border border-border bg-secondary/60 hover:border-primary/50 hover:bg-primary/5 transition-all text-center group cursor-pointer focus-visible:outline-2 focus-visible:outline-primary shadow-xs"
                  >
                    <LinuxIcon className="h-5 w-5 text-accent group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">Linux x64</span>
                    <span className="font-mono text-[10px] text-muted-foreground mt-0.5">Ubuntu Binary (48.3MB)</span>
                  </a>

                  {/* macOS */}
                  <a
                    href={`https://github.com/RohannShetty/gitbook-downloader/releases/download/${release.tag}/docharvest-macos-latest`}
                    className="flex flex-col items-center justify-center p-3.5 rounded-lg border border-border bg-secondary/60 hover:border-primary/50 hover:bg-primary/5 transition-all text-center group cursor-pointer focus-visible:outline-2 focus-visible:outline-primary shadow-xs"
                  >
                    <AppleIcon className="h-5 w-5 text-cyan group-hover:scale-110 transition-transform mb-1.5" />
                    <span className="font-mono text-xs font-bold text-foreground">macOS</span>
                    <span className="font-mono text-[10px] text-muted-foreground mt-0.5">Apple/Intel (30.4MB)</span>
                  </a>
                </div>
              </div>

              {/* SHA256 Verification Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono text-muted-foreground border-t border-border pt-4 bg-muted/20 -mx-6 -mb-6 p-4 sm:px-6 rounded-b-xl">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald shrink-0" />
                  <span>Signed &amp; verified with SHA-256 in GitHub Actions CI.</span>
                </div>

                <button
                  onClick={handleCopyVerify}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-secondary hover:bg-primary/10 hover:text-primary transition-colors text-[11px] font-semibold text-foreground shrink-0 cursor-pointer focus-visible:outline-2 focus-visible:outline-primary border border-border"
                  title="Copy PowerShell verification command"
                  aria-label="Copy SHA-256 verification command"
                >
                  {copiedVerify ? <Check className="h-3 w-3 text-cyan/50" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedVerify ? 'Copied' : 'Copy Hash Check'}</span>
                </button>
              </div>

            </div>
          </div>

          {/* Right Column: Live Commit Log Stream */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-2 font-mono text-xs">
              <span className="font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                <GitCommit className="h-4 w-4 text-cyan" />
                <span>Recent Commit Stream (master)</span>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-card/50 text-emerald border border-border/50">
                LIVE
              </span>
            </div>

            <div className="border border-border rounded-xl bg-card divide-y divide-border-border/60 max-h-[500px] overflow-y-auto shadow-md">
              {commits.map((commit, index) => (
                <div
                  key={commit.sha + index}
                  className="p-3.5 flex gap-3 text-xs font-mono group hover:bg-secondary/40 transition-colors"
                >
                  <button
                    onClick={() => handleCopySha(commit.sha)}
                    className="text-cyan pt-0.5 select-none font-bold hover:underline cursor-pointer focus-visible:outline-2 focus-visible:outline-primary flex items-center gap-1 shrink-0"
                    title="Click to copy commit hash"
                    aria-label="Copy commit hash"
                  >
                    <span>[{commit.sha}]</span>
                    {copiedSha === commit.sha && <Check className="h-3 w-3 text-cyan/50" />}
                  </button>

                  <div className="flex-1 space-y-1 overflow-hidden">
                    <a
                      href={commit.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-foreground leading-snug font-medium group-hover:text-primary transition-colors block truncate"
                      title={commit.message}
                    >
                      {commit.message}
                    </a>
                    <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                      <span className="text-foreground font-medium">{commit.author}</span>
                      <span>•</span>
                      <span>{commit.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-lg bg-muted/40 border border-border text-[11px] font-mono text-muted-foreground flex items-center justify-between">
              <span>Branch: <strong className="text-foreground">master</strong> (Clean &amp; Passing)</span>
              <a
                href="https://github.com/RohannShetty/gitbook-downloader/commits/master"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline font-semibold"
              >
                View Full Log →
              </a>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
