'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { GitBranch, GitCommit, Star, GitFork, ExternalLink, Calendar } from 'lucide-react';
import { GithubUserData, GithubRepoData, GithubCommitData } from '@/lib/github';

interface GithubFeedProps {
  profile: GithubUserData;
  repos: GithubRepoData[];
  commits: GithubCommitData[];
}

// Generate mock contribution graph blocks for the mini heatmap
const generateHeatmap = () => {
  const intensities = [0, 1, 2, 3, 0, 1, 3, 2, 4, 1, 0, 2, 4, 3, 0, 1, 2, 0, 3, 4, 2, 1, 0, 3];
  const colors = [
    'bg-zinc-900 border-zinc-800/80', // 0
    'bg-indigo-950/40 border-indigo-900/30', // 1
    'bg-indigo-900/60 border-indigo-800/40', // 2
    'bg-indigo-800/80 border-indigo-700/60', // 3
    'bg-primary border-indigo-500/80', // 4
  ];
  return intensities.map((intensity, i) => (
    <div
      key={i}
      className={`w-3.5 h-3.5 rounded-sm border ${colors[intensity]} transition-colors hover:scale-110 duration-150`}
      title={`Activity level: ${intensity}`}
    />
  ));
};

export default function GithubFeed({ profile, repos, commits }: GithubFeedProps) {
  return (
    <section id="github" className="border-b border-border bg-background py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 04 / GITHUB INTEGRATION
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
              Live Activity Telemetry
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-xl">
              Real-time commit logs, contribution vectors, and star metrics fetched from the GitHub API.
            </p>
          </div>
          
          {/* User Profile Summary */}
          <div className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card/40 backdrop-blur-sm">
            <img
              src={profile.avatar_url}
              alt={profile.name}
              className="w-10 h-10 rounded-full border border-border"
            />
            <div className="flex flex-col">
              <span className="text-xs font-bold font-mono text-foreground">
                @{profile.login}
              </span>
              <a
                href={profile.html_url}
                target="_blank"
                rel="noreferrer"
                className="text-[10px] font-mono text-primary hover:underline flex items-center gap-1"
              >
                <span>View Profile</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Recent Commits Log (Left Columns) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-2">
              <span className="font-mono text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                <GitCommit className="h-4 w-4 text-primary animate-pulse" />
                <span>Recent Commit Stream</span>
              </span>
              <span className="font-mono text-[10px] text-muted-foreground">LIMIT: 12_EVENTS</span>
            </div>

            <div className="border border-border rounded-xl bg-card/20 divide-y divide-border/60 max-h-[460px] overflow-y-auto pr-1">
              {commits.map((commit, index) => (
                <div key={commit.sha + index} className="p-4 flex gap-3 text-xs font-mono group hover:bg-card/40 transition-colors">
                  <div className="text-primary pt-0.5 select-none font-bold">
                    [{commit.sha}]
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="text-foreground leading-snug line-clamp-2">
                      {commit.message}
                    </p>
                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                      <span className="text-accent font-semibold">{commit.repo_name}</span>
                      <span>•</span>
                      <span>{commit.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Repositories & Heatmap (Right Columns) */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Top Repositories Grid */}
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-border/80 pb-2">
                <span className="font-mono text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-accent" />
                  <span>Top Repositories</span>
                </span>
              </div>

              <div className="space-y-3">
                {repos.map((repo) => (
                  <a
                    key={repo.id}
                    href={repo.html_url}
                    target="_blank"
                    rel="noreferrer"
                    className="block p-4 border border-border bg-card hover:border-primary/50 hover:bg-card/80 rounded-xl transition-all duration-200"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h4 className="font-mono text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                        {repo.name}
                      </h4>
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground shrink-0 font-mono">
                        <span className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-amber-500 fill-amber-500/20" />
                          {repo.stargazers_count}
                        </span>
                        <span className="flex items-center gap-1">
                          <GitFork className="h-3 w-3 text-indigo-400" />
                          {repo.forks_count}
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-muted-foreground font-mono mt-1.5 line-clamp-2">
                      {repo.description}
                    </p>
                  </a>
                ))}
              </div>
            </div>

            {/* Heatmap Section */}
            <div className="p-4 border border-border rounded-xl bg-card/30 space-y-3">
              <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block">
                Activity Density Grid
              </span>
              <div className="grid grid-cols-8 sm:grid-cols-12 gap-1.5 w-fit">
                {generateHeatmap()}
              </div>
              <div className="flex items-center justify-between font-mono text-[9px] text-muted-foreground border-t border-border/50 pt-2">
                <span>Less</span>
                <div className="flex gap-1">
                  <div className="w-2.5 h-2.5 rounded bg-zinc-900 border border-zinc-800" />
                  <div className="w-2.5 h-2.5 rounded bg-indigo-900 border border-indigo-850" />
                  <div className="w-2.5 h-2.5 rounded bg-indigo-800 border border-indigo-750" />
                  <div className="w-2.5 h-2.5 rounded bg-primary border border-indigo-500" />
                </div>
                <span>More</span>
              </div>
            </div>

          </div>

        </div>
      </div>
    </section>
  );
}
