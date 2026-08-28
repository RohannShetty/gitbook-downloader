'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, BookOpen, Server, CheckCircle2, ArrowRight } from 'lucide-react';

const PERSONAS = [
  {
    id: "ai",
    title: "AI & RAG Engineers",
    icon: Bot,
    iconBg: "bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border-cyan-500/30",
    badge: "Vector & Agent Ready",
    pain: "LLMs hallucinate on outdated training data. Scraping docs with curl dumps 40KB+ HTML noise that exhausts context windows.",
    solution: "DocHarvest compiles clean vector JSONL datasets with token counts, SHA-256 hashes, and standard llms.txt manifests for instant agent indexing.",
    highlights: [
      "Zero noise (89% prompt token reduction)",
      "Direct drop-in for LangChain & ChromaDB",
      "FastMCP server for Cursor & Claude Desktop"
    ]
  },
  {
    id: "offline",
    title: "Offline Developers & Researchers",
    icon: BookOpen,
    iconBg: "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30",
    badge: "Air-Gapped Portability",
    pain: "Reading documentation on flights, during outages, or in secure air-gapped enterprise environments is painful with fragmented web pages.",
    solution: "Merges 500+ documentation pages into a single consolidated book.md and publication-grade PDF handbook with automated table of contents.",
    highlights: [
      "Pure-Python PDF generation (zero C-deps)",
      "Embedded SQLite FTS5 search (<15ms queries)",
      "Standalone desktop GUI (docharvest.exe)"
    ]
  },
  {
    id: "devops",
    title: "DevOps & Archival Teams",
    icon: Server,
    iconBg: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30",
    badge: "Automated Synchronization",
    pain: "Docs change across releases without changelog notices. Mirroring docs locally often hits rate limits or gets blocked by Cloudflare.",
    solution: "Heuristic crawlers with cross-platform lock recovery, retry adapters, exponential backoffs, and automated Git diff tracking.",
    highlights: [
      "Semver snapshot diffs across crawls",
      "Auto-recovering PID domain locks",
      "Headless CLI automation in CI/CD"
    ]
  }
];

export function PersonaShowcase() {
  return (
    <section className="border-b border-border bg-background py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 06 / BUILT FOR YOUR WORKFLOW
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Three Specialized Workflows. Zero Friction.
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Whether you are training embeddings, coding on a plane, or managing documentation backups in CI/CD.
          </p>
        </div>

        {/* 3 Persona Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PERSONAS.map((persona) => {
            const Icon = persona.icon;
            return (
              <div
                key={persona.id}
                className="flex flex-col justify-between border border-border bg-card rounded-xl p-6 sm:p-7 shadow-lg space-y-6 hover:border-primary/40 transition-all duration-200"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className={`p-2.5 rounded-lg border ${persona.iconBg}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="font-mono text-[9px] px-2 py-0.5 rounded bg-background border border-border text-foreground font-bold">
                      {persona.badge}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-foreground">
                    {persona.title}
                  </h3>

                  <div className="space-y-3 text-xs font-mono leading-relaxed pt-1">
                    <div className="space-y-1">
                      <span className="text-rose-600 dark:text-rose-400 font-bold text-[11px] block">Problem:</span>
                      <p className="text-muted-foreground text-[11px] leading-relaxed">{persona.pain}</p>
                    </div>

                    <div className="space-y-1 pt-1 border-t border-border/40">
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold text-[11px] block">DocHarvest Solution:</span>
                      <p className="text-muted-foreground text-[11px] leading-relaxed">{persona.solution}</p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-border/80 pt-4 space-y-2">
                  <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block font-semibold">
                    Core Advantages:
                  </span>
                  <ul className="space-y-1.5 text-xs font-mono text-muted-foreground">
                    {persona.highlights.map((h, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400 shrink-0" />
                        <span className="text-foreground/90">{h}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
