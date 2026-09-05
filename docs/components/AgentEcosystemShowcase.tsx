'use client';

import React, { useState } from 'react';
import { Bot, Copy, Check, Zap } from 'lucide-react';
import { AI_AGENTS } from '@/data/showcaseData';
import { STATS } from '../lib/stats';


const CATEGORIES = ['All', 'AI IDE', 'Terminal Agent', 'CLI Harness', 'Extension'] as const;

export function AgentEcosystemShowcase() {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('cursor');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [copied, setCopied] = useState<boolean>(false);
  const [copiedCli, setCopiedCli] = useState<boolean>(false);

  const selectedAgent = AI_AGENTS.find((a) => a.id === selectedAgentId) || AI_AGENTS[0];

  const filteredAgents = selectedCategory === 'All'
    ? AI_AGENTS
    : AI_AGENTS.filter((a) => a.category === selectedCategory);

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedAgent.configSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyCli = () => {
    navigator.clipboard.writeText(selectedAgent.cliCommand);
    setCopiedCli(true);
    setTimeout(() => setCopiedCli(false), 2000);
  };


  return (
    <section id="agents" className="border-b border-border bg-card/10 py-16 scroll-mt-16">
      <div className="mx-auto max-w-7x px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-10">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase flex items-center gap-1.5">
              <Bot className="h-4 w-4 text-cyan" />
              <span>Supported IDEs &amp; AI Coding Agents</span>
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Native FastMCP Server for {STATS.agentsShipped}+ Modern Coding Harnesses
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Plug DocHarvest directly into Cursor, Claude Code, OpenCode, Pi, Windsurf, or Codex. Your agents gain 12 native tools to crawl, index, and query documentation on demand over stdio.
          </p>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2 mb-8">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg border font-mono text-xs font-semibold transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                selectedCategory === cat
                  ? 'border-border/50 bg-card/50 text-cyan font-bold shadow-xs'
                  : 'border-border bg-card text-muted-foreground hover:text-foreground'
              }`}
            >
              {cat === 'All' ? `All ${STATS.agentsShipped}+ Harnesses` : cat + 's'}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Agent Grid Selector */}
          <div className="lg:col-span-5 space-y-2.5 max-h-[580px] overflow-y-auto pr-1">
            {filteredAgents.map((agent) => {
              const isSelected = agent.id === selectedAgent.id;
              return (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgentId(agent.id)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary flex items-center justify-between group ${
                    isSelected
                      ? 'border-border/50 bg-cyan/10 text-foreground shadow-md'
                      : 'border-border bg-card hover:border-border/90 text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-foreground group-hover:text-primary transition-colors">
                        {agent.name}
                      </span>
                      <span className="font-mono text-[9px] px-1.5 py-0.5 rounded bg-background border border-border text-muted-foreground">
                        {agent.category}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {agent.description}
                    </p>
                  </div>

                  <span className={`font-mono text-[10px] px-2 py-0.5 rounded-full border ${
                    isSelected
                      ? 'border-border/50 bg-card/50 text-cyan font-bold'
                      : 'border-border/60 bg-secondary text-muted-foreground'
                  }`}>
                    {agent.badge}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Right Column: Active Agent Deep-Dive & Config Box */}
          <div className="lg:col-span-7 space-y-5">
            <div className="border border-border rounded-xl bg-card p-6 shadow-xl space-y-6">
              
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-foreground">
                      {selectedAgent.name}
                    </h3>
                    <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-semibold">
                      {selectedAgent.category}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-muted-foreground">
                    Configuration File: <code className="text-cyan font-bold">{selectedAgent.configPath}</code>
                  </p>
                </div>

                <button
                  onClick={handleCopy}
                  className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground font-mono text-xs font-semibold hover:bg-primary/90 transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary shadow-sm shrink-0"
                  aria-label="Copy FastMCP configuration"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-white" /> : <Copy className="h-3.5 w-3.5 text-white" />}
                  <span>{copied ? 'Config Copied' : 'Copy FastMCP JSON'}</span>
                </button>
              </div>

              {/* JSON Configuration Snippet */}
              <div className="space-y-2">
                <div className="flex items-center justify-between font-mono text-[11px] text-muted-foreground">
                  <span>1-Click FastMCP Configuration Snippet:</span>
                  <span>stdio protocol</span>
                </div>
                <div className="p-4 rounded-lg bg-card/95 border border-border/80 font-mono text-xs leading-relaxed overflow-x-auto shadow-inner">
                  <pre><code>{selectedAgent.configSnippet}</code></pre>
                </div>
              </div>

              {/* CLI Execution Command */}
              <div className="space-y-2">
                <div className="flex items-center justify-between font-mono text-[11px] text-muted-foreground">
                  <span>Direct CLI Invocation:</span>
                  <button
                    onClick={handleCopyCli}
                    className="text-primary hover:underline inline-flex items-center gap-1 cursor-pointer focus-visible:outline-2 focus-visible:outline-primary font-semibold"
                    aria-label="Copy CLI command"
                  >
                    {copiedCli ? <Check className="h-3 w-3 text-cyan" /> : <Copy className="h-3 w-3" />}
                    <span>{copiedCli ? 'Copied' : 'Copy CLI'}</span>
                  </button>
                </div>
                <div className="px-3.5 py-2.5 rounded-lg bg-card/95 border border-border/80 font-mono text-xs text-foreground flex items-center justify-between overflow-x-auto">
                  <code>$ {selectedAgent.cliCommand}</code>
                </div>
              </div>


              {/* Highlights & Features */}
              <div className="space-y-2 border-t border-border/80 pt-4">
                <span className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider block">
                  Agent Capabilities with DocHarvest:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  {selectedAgent.highlights.map((h, i) => (
                    <div key={i} className="p-2.5 rounded-lg border border-border/60 bg-background/50 font-mono text-[11px] text-foreground flex items-start gap-1.5">
                      <Zap className="h-3.5 w-3.5 text-cyan shrink-0 mt-0.5" />
                      <span>{h}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>


        </div>

      </div>
    </section>
  );
}
