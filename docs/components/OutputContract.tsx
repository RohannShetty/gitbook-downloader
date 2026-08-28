'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CONTRACT_FORMATS } from '../data/showcaseData';
import { FileText, Database, FileCode, BookOpen, CheckCircle2, ArrowRight } from 'lucide-react';

const formatIcons: Record<string, React.ComponentType<any>> = {
  markdown: FileText,
  rag: Database,
  llmstxt: FileCode,
  pdf: BookOpen,
};

export function OutputContract() {
  const [selectedFormat, setSelectedFormat] = useState(CONTRACT_FORMATS[0]);
  const IconComponent = formatIcons[selectedFormat.id] || FileText;

  return (
    <section id="contract" className="border-b border-border bg-background py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              The Four-Part Output Contract
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            One Crawl. Four Production-Ready Formats.
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Every crawl emits a predictable four-part output matrix ready for Claude, Cursor, vector databases, and offline reading.
          </p>
        </div>

        {/* 4 Format Selector Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {CONTRACT_FORMATS.map((fmt) => {
            const isSelected = selectedFormat.id === fmt.id;
            const FmtIcon = formatIcons[fmt.id] || FileText;

            return (
              <button
                key={fmt.id}
                onClick={() => setSelectedFormat(fmt)}
                className={`p-5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between h-[160px] ${
                  isSelected
                    ? 'border-primary bg-primary/10 shadow-lg'
                    : 'border-border bg-card hover:border-primary/40 hover:bg-secondary/40'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <FmtIcon className={`h-5 w-5 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                    <span className="font-mono text-[9px] px-2 py-0.5 rounded bg-background border border-border text-foreground font-bold">
                      .{fmt.fileExt}
                    </span>
                  </div>
                  <h3 className="font-mono text-sm font-bold text-foreground">
                    {fmt.title}
                  </h3>
                </div>
                <p className="text-[11px] text-muted-foreground font-mono line-clamp-2">
                  {fmt.subtitle}
                </p>
              </button>
            );
          })}
        </div>

        {/* Active Format Deep Dive */}
        <motion.div
          key={selectedFormat.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="border border-border rounded-xl bg-card p-6 sm:p-8 shadow-xl"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left: Spec Details */}
            <div className="lg:col-span-7 space-y-4">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 font-bold uppercase">
                  {selectedFormat.badge}
                </span>
                <span className="font-mono text-[10px] text-muted-foreground">
                  FILE: {selectedFormat.fileExt}
                </span>
              </div>

              <h3 className="text-2xl font-bold text-foreground">
                {selectedFormat.title} — {selectedFormat.subtitle}
              </h3>

              <p className="text-xs text-muted-foreground font-mono leading-relaxed">
                {selectedFormat.description}
              </p>

              <div className="space-y-2 pt-2">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block">
                  Contract Guarantees:
                </span>
                <ul className="space-y-2 text-xs font-mono text-muted-foreground">
                  {selectedFormat.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Right: Architectural Mock Display */}
            <div className="lg:col-span-5 flex justify-center">
              <div className="w-full max-w-sm border border-border rounded-xl bg-[#09090c] p-5 font-mono text-xs space-y-3 shadow-inner">
                <div className="flex items-center justify-between border-b border-border/80 pb-2 text-[10px] text-muted-foreground">
                  <span>TARGET: {selectedFormat.fileExt}</span>
                  <span className="text-emerald-400">READY</span>
                </div>
                <div className="text-zinc-300 text-[11px] leading-relaxed space-y-2">
                  <div className="text-cyan-400 font-bold">$ docharvest export --format {selectedFormat.id}</div>
                  <div className="text-muted-foreground text-[10px]">
                    ✓ Synthesized AST nodes into uniform format.<br/>
                    ✓ Injected SHA-256 cryptographic hashes.<br/>
                    ✓ Output written to disk in 0.4s.
                  </div>
                </div>
              </div>
            </div>

          </div>
        </motion.div>

      </div>
    </section>
  );
}
