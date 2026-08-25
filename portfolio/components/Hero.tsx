'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Terminal, BookOpen, Layers } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border bg-background py-20 lg:py-32">
      {/* Drafting Board Architectural Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />
      
      {/* Accent Light Glows */}
      <div className="absolute top-0 left-1/4 h-[350px] w-[350px] bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 h-[250px] w-[250px] bg-accent/5 rounded-full blur-[80px] pointer-events-none" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Headline and Copy */}
          <div className="lg:col-span-7 flex flex-col items-start text-left space-y-6">
            {/* Tagline Badge */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-secondary/80 backdrop-blur-md text-xs font-mono text-muted-foreground"
            >
              <Terminal className="h-3 w-3 text-primary animate-pulse" />
              <span>const status = &quot;Bridging Structure &amp; Syntax&quot;;</span>
            </motion.div>

            {/* Core Value Proposition */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.05] text-foreground"
            >
              Engineering <span className="text-primary">computational tools</span> with an <span className="text-accent">architectural</span> perspective.
            </motion.h1>

            {/* Subheading describing the dual discipline */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-base sm:text-lg text-muted-foreground font-mono leading-relaxed max-w-2xl"
            >
              Architectural designer turned software developer. I craft developer tooling, execution engines, and local AI agent integrations, applying structural design discipline to digital systems.
            </motion.p>

            {/* Primary & Secondary Call to Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-wrap items-center gap-4 w-full pt-4"
            >
              <a
                href="#projects"
                className="group inline-flex h-11 items-center justify-center rounded-lg bg-primary px-6 text-xs font-mono font-bold text-primary-foreground hover:bg-primary/95 shadow-md hover:shadow-primary/10 transition-all duration-200"
              >
                View My Work
                <ArrowRight className="ml-2 h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
              </a>

              <a
                href="#blog"
                className="inline-flex h-11 items-center justify-center rounded-lg border border-border bg-background px-6 text-xs font-mono font-bold text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all duration-200"
              >
                Read My Writing
              </a>
            </motion.div>
          </div>

          {/* Interactive Spatial Diagram (Architectural blueprint style) */}
          <div className="lg:col-span-5 relative flex items-center justify-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="w-full aspect-square max-w-[400px] border border-border rounded-xl bg-card/40 backdrop-blur-xl relative overflow-hidden flex flex-col p-6 shadow-xl"
            >
              {/* Drafting grid alignment marks */}
              <div className="absolute top-2 left-2 font-mono text-[9px] text-muted-foreground/60 select-none">GRID: 10px</div>
              <div className="absolute bottom-2 right-2 font-mono text-[9px] text-muted-foreground/60 select-none">COORD: [39.02, 12.85]</div>

              {/* Wireframe structure */}
              <div className="flex-1 relative border border-dashed border-border/80 rounded-lg flex items-center justify-center">
                {/* Concentric isometric shapes representing structure & syntax */}
                <svg className="w-full h-full p-4 text-muted-foreground/40" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                  {/* Axis lines */}
                  <line x1="10" y1="100" x2="190" y2="100" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 2" />
                  <line x1="100" y1="10" x2="100" y2="190" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 2" />
                  
                  {/* Isometric box wireframe */}
                  <polygon points="100,30 160,65 160,135 100,170 40,135 40,65" stroke="currentColor" strokeWidth="0.75" />
                  <polygon points="100,70 140,93 140,140 100,163 60,140 60,93" stroke="var(--primary)" strokeWidth="1" strokeOpacity="0.8" />
                  
                  {/* Connective lines */}
                  <line x1="100" y1="30" x2="100" y2="170" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="40" y1="65" x2="160" y2="135" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="160" y1="65" x2="40" y2="135" stroke="currentColor" strokeWidth="0.5" />

                  {/* Corner dots */}
                  <circle cx="100" cy="30" r="2.5" fill="var(--accent)" />
                  <circle cx="160" cy="65" r="2.5" fill="var(--accent)" />
                  <circle cx="160" cy="135" r="2.5" fill="var(--accent)" />
                  <circle cx="100" cy="170" r="2.5" fill="var(--accent)" />
                  <circle cx="40" cy="135" r="2.5" fill="var(--accent)" />
                  <circle cx="40" cy="65" r="2.5" fill="var(--accent)" />
                </svg>

                {/* Animated tech badges on top of canvas */}
                <div className="absolute top-6 left-6 p-2 rounded border border-border bg-background/90 shadow-md flex items-center gap-1.5 font-mono text-[9px] text-foreground select-none">
                  <Layers className="h-3.5 w-3.5 text-primary" />
                  <span>Spatial design</span>
                </div>

                <div className="absolute bottom-6 right-6 p-2 rounded border border-border bg-background/90 shadow-md flex items-center gap-1.5 font-mono text-[9px] text-foreground select-none">
                  <Terminal className="h-3.5 w-3.5 text-accent" />
                  <span>Systems code</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
