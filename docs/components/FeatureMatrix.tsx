'use client';

import React from 'react';
import { Check, X, Sparkles } from 'lucide-react';

const MATRIX_ROWS = [
  {
    feature: "Native AST Heuristic Framework Detection (GitBook, Mintlify, Docusaurus)",
    docharvest: true,
    rawScrapers: false,
    cloudApis: "Partial",
    detail: "Automatically isolates article DOMs and probes raw markdown endpoints directly."
  },
  {
    feature: "Zero HTML/JSX Soup in Markdown Output",
    docharvest: true,
    rawScrapers: false,
    cloudApis: true,
    detail: "Strips cookie banners, navbars, sidebars, and interactive widget code."
  },
  {
    feature: "Standard llms.txt & Vector RAG JSONL Compilation",
    docharvest: true,
    rawScrapers: false,
    cloudApis: false,
    detail: "Builds unified RAG chunk files with token counts and SHA-256 content hashes."
  },
  {
    feature: "Pure-Python PDF Handbook Generation with TOC (fpdf2)",
    docharvest: true,
    rawScrapers: false,
    cloudApis: false,
    detail: "Zero external C-library dependencies (no WeasyPrint or wkhtmltopdf)."
  },
  {
    feature: "Built-in FastMCP v2 Server for Cursor, Claude Code & 14 AI IDEs",
    docharvest: true,
    rawScrapers: false,
    cloudApis: "API Key Req",
    detail: "10 native MCP tools, resources & prompts running over stdio directly inside your agent."
  },
  {
    feature: "Embedded SQLite FTS5 BM25 Full-Text Search Database",
    docharvest: true,
    rawScrapers: false,
    cloudApis: false,
    detail: "Instant sub-15ms keyword search queries across thousands of harvested pages."
  },
  {
    feature: "100% Free, Open Source (MIT) & Local Privacy",
    docharvest: true,
    rawScrapers: true,
    cloudApis: false,
    detail: "No subscription fees, no credit limits, and zero data leaves your local machine."
  }
];

export function FeatureMatrix() {
  return (
    <section id="matrix" className="border-b border-border bg-background py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 04 / CAPABILITY COMPARISON
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Why DocHarvest Outperforms Raw Scrapers &amp; Cloud APIs
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Compare DocHarvest against raw scrapers and proprietary cloud services.
          </p>
        </div>

        {/* Feature Comparison Table */}
        <div className="border border-border rounded-xl bg-card overflow-x-auto shadow-xl">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-border bg-zinc-950/80">
                <th className="p-4 sm:p-5 text-foreground font-bold w-1/2">
                  Engine Capability
                </th>
                <th className="p-4 sm:p-5 text-cyan-400 font-bold bg-cyan-500/5 text-center">
                  DocHarvest v11.0.0
                </th>
                <th className="p-4 sm:p-5 text-zinc-400 font-semibold text-center hidden sm:table-cell">
                  Raw Scrapers (curl/Scrapy)
                </th>
                <th className="p-4 sm:p-5 text-zinc-400 font-semibold text-center">
                  Cloud Reader APIs
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {MATRIX_ROWS.map((row, index) => (
                <tr key={index} className="hover:bg-secondary/30 transition-colors">
                  <td className="p-4 sm:p-5">
                    <div className="font-bold text-foreground">{row.feature}</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5 font-normal">
                      {row.detail}
                    </div>
                  </td>
                  
                  {/* DocHarvest Column */}
                  <td className="p-4 sm:p-5 text-center bg-cyan-500/5">
                    {row.docharvest ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-emerald-500/20 text-emerald-400">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : (
                      <X className="h-4 w-4 text-rose-500 mx-auto" />
                    )}
                  </td>

                  {/* Raw Scrapers Column */}
                  <td className="p-4 sm:p-5 text-center hidden sm:table-cell">
                    {row.rawScrapers === true ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-emerald-500/10 text-emerald-400">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-rose-500/10 text-rose-500">
                        <X className="h-4 w-4" />
                      </div>
                    )}
                  </td>

                  {/* Cloud APIs Column */}
                  <td className="p-4 sm:p-5 text-center">
                    {row.cloudApis === true ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-emerald-500/10 text-emerald-400">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : row.cloudApis === false ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-rose-500/10 text-rose-500">
                        <X className="h-4 w-4" />
                      </div>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {row.cloudApis}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </section>
  );
}
