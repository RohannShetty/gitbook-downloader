'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { DOC_FRAMEWORKS, DocFramework } from '../data/showcaseData';
import { CheckCircle2, Globe, Sparkles, Layers, ArrowRight, Code } from 'lucide-react';

export function DocTypeSelector() {
  const [selectedFramework, setSelectedFramework] = useState<DocFramework>(DOC_FRAMEWORKS[0]);

  return (
    <section id="platforms" className="border-b border-border bg-card/20 py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              Framework Intelligence
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Engineered For Every Major Documentation Platform
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            DocHarvest uses dynamic heuristics to detect documentation frameworks, bypassing DOM noise to extract author-original markdown directly.
          </p>
        </div>

        {/* Framework Selector Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 mb-8">
          {DOC_FRAMEWORKS.map((framework) => {
            const isSelected = selectedFramework.id === framework.id;
            return (
              <button
                key={framework.id}
                onClick={() => setSelectedFramework(framework)}
                aria-pressed={isSelected}
                className={`p-3 rounded-lg border font-mono text-xs font-bold text-center transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                  isSelected
                    ? 'border-primary bg-primary/10 text-primary shadow-sm'
                    : 'border-border bg-card/40 text-muted-foreground hover:bg-card hover:text-foreground'
                }`}
              >
                <div>{framework.name}</div>
                <div className="text-[9px] font-normal text-muted-foreground mt-0.5 truncate">
                  {framework.badge}
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Framework Detailed Inspection Board */}
        <motion.div
          key={selectedFramework.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="border border-border rounded-xl bg-card/60 p-6 sm:p-8 shadow-xl"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Heuristic Spec & Key Features */}
            <div className="lg:col-span-5 space-y-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono border border/50 bg/50 text-cyan font-bold uppercase">
                    {selectedFramework.badge}
                  </span>
                  <span className="font-mono text-[10px] text-muted-foreground">
                    PRIORITY: {selectedFramework.detectionPriority}/100
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-foreground">
                  {selectedFramework.name} Harvesting Heuristics
                </h3>
                <p className="text-xs text-muted-foreground font-mono leading-relaxed">
                  {selectedFramework.description}
                </p>
              </div>

              {/* Sample Target URL */}
              <div className="p-3 rounded-lg border border-border bg-background font-mono text-xs space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1 font-semibold">
                  <Globe className="h-3 w-3 text-primary" /> Target Sample:
                </span>
                <div className="text-foreground text-[11px] truncate font-semibold">
                  {selectedFramework.sampleUrl}
                </div>
              </div>

              {/* Feature Checklist */}
              <div className="space-y-2">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block font-semibold">
                  Parsing Capabilities:
                </span>
                <ul className="space-y-2 text-xs font-mono text-muted-foreground">
                  {selectedFramework.features.map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald shrink-0 mt-0.5" />
                      <span className="text-foreground/90">{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Right Column: Code Comparison (Raw HTML vs Clean Markdown) */}
            <div className="lg:col-span-7 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Raw HTML Soup */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between font-mono text-[10px] text-destructive font-bold">
                    <span>❌ Raw Scraper / Curl (HTML Noise)</span>
                    <span>~42.8 KB</span>
                  </div>
                  <pre className="h-[260px] overflow-y-auto text-[10px] text/40 bg/95 p-3 rounded-lg border border-destructive/30">
                    <code>{selectedFramework.rawHtmlSnippet}</code>
                  </pre>
                </div>

                {/* Clean Markdown Output */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between font-mono text-[10px] text-emerald font-bold">
                    <span>✓ DocHarvest Output (LLM Context)</span>
                    <span>~3.2 KB Clean</span>
                  </div>
                  <pre className="h-[260px] overflow-y-auto text-[10px] text/30 bg/95 p-3 rounded-lg border border-emerald/30">
                    <code>{selectedFramework.cleanMarkdownSnippet}</code>
                  </pre>
                </div>

              </div>
            </div>

          </div>
        </motion.div>

      </div>
    </section>
  );
}
