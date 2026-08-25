'use client';

import React from 'react';
import { Mail, Activity, Eye, Zap } from 'lucide-react';
import { GithubIcon, LinkedinIcon, TwitterIcon } from './Icons';

export default function About() {
  return (
    <section id="about" className="border-b border-border bg-background/50 py-20 relative scroll-mt-16">
      {/* Structural layout lines */}
      <div className="absolute top-0 bottom-0 left-[8%] border-l border-border/40 pointer-events-none hidden lg:block" />
      <div className="absolute top-0 bottom-0 right-[8%] border-r border-border/40 pointer-events-none hidden lg:block" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
          {/* Conceptual Image / Blueprint Showcase Block */}
          <div className="lg:col-span-5 flex flex-col justify-center items-center">
            <div className="relative w-full aspect-[4/5] rounded-xl border border-border bg-card overflow-hidden group shadow-lg">
              {/* Drafting background blueprint style */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:1.5rem_1.5rem]" />
              
              <div className="absolute inset-0 flex flex-col p-6 items-start justify-between z-10">
                {/* Structural labels */}
                <div className="font-mono text-[9px] text-muted-foreground tracking-widest uppercase">
                  PLAN / ELEVATION / SEC
                </div>
                
                {/* Mock drafting box representing author */}
                <div className="w-full flex-1 flex items-center justify-center py-6">
                  <div className="w-4/5 aspect-[4/5] max-h-[220px] border border-dashed border-primary/50 relative flex items-center justify-center">
                    <div className="absolute inset-0 bg-primary/5 group-hover:bg-primary/10 transition-colors" />
                    
                    {/* Diagnostic crosses */}
                    <div className="absolute top-0 bottom-0 left-1/2 border-l border-primary/30" />
                    <div className="absolute left-0 right-0 top-1/2 border-t border-primary/30" />
                    
                    <span className="font-mono text-xs font-bold text-foreground bg-background px-3 py-1 border border-border rounded z-20 group-hover:border-primary/50 transition-colors">
                      [ROHAN SHETTY]
                    </span>
                  </div>
                </div>

                {/* Status Bar */}
                <div className="w-full flex items-center justify-between font-mono text-[9px] text-muted-foreground border-t border-border/80 pt-3">
                  <div className="flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                    <span>SYSTEMS: ONLINE</span>
                  </div>
                  <span>LOC: BLR, IN</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bio Narrative */}
          <div className="lg:col-span-7 flex flex-col justify-center space-y-6">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
                // 01 / BIOGRAPHY
              </span>
              <div className="h-px flex-1 bg-border/80" />
            </div>

            <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
              Bridging spatial structure and computational logic.
            </h2>

            <div className="space-y-4 text-sm text-muted-foreground leading-relaxed font-mono">
              <p>
                My background is in architectural design, where I trained to solve complex physical problems by balancing structural integrity, spatial efficiency, and human interaction. Today, I translate that same structural rigor into building robust software systems.
              </p>
              <p>
                As a developer, I specialize in developer tools, local execution environments, and automated data compilation pipelines. I build tools that automate tedious developer workflows—such as <span className="text-foreground font-semibold">OpenAlgo</span> (quantitative execution engines), <span className="text-foreground font-semibold">ShettyBot</span> (operational workflow automations), and <span className="text-foreground font-semibold">DocHarvest</span> (unified AST document harvesting).
              </p>
              <p>
                When I&apos;m not writing code or architectural scripts, I&apos;m exploring fitness, self-hosting productivity workflows, and optimizing developer setups with local AI models (such as customized Claude CLI modules).
              </p>
            </div>

            {/* Social Connect Matrix */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
              <div className="flex flex-col gap-2">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider">
                  Social Channels
                </span>
                <div className="flex gap-2">
                  <a
                    href="https://github.com/rohannshetty"
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg border border-border bg-secondary hover:bg-primary hover:text-white transition-all duration-200"
                    title="GitHub"
                  >
                    <GithubIcon className="h-4 w-4" />
                  </a>
                  <a
                    href="https://linkedin.com/in/rohannshetty"
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg border border-border bg-secondary hover:bg-primary hover:text-white transition-all duration-200"
                    title="LinkedIn"
                  >
                    <LinkedinIcon className="h-4 w-4" />
                  </a>
                  <a
                    href="https://twitter.com/rohannshetty"
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg border border-border bg-secondary hover:bg-primary hover:text-white transition-all duration-200"
                    title="Twitter"
                  >
                    <TwitterIcon className="h-4 w-4" />
                  </a>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider">
                  Direct Contact
                </span>
                <a
                  href="mailto:shettyrohan2@gmail.com"
                  className="inline-flex items-center gap-2 text-xs font-mono font-semibold text-foreground hover:text-primary transition-colors mt-2"
                >
                  <Mail className="h-4 w-4 text-primary" />
                  <span>shettyrohan2@gmail.com</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
