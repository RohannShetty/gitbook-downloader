'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Code2, Cpu, Wrench, Palette, Database } from 'lucide-react';

interface Skill {
  name: string;
  level: number; // 1 to 5 (subtle details, not percentage bar)
  status: 'active' | 'experimenting';
}

interface SkillCategory {
  title: string;
  icon: React.ComponentType<any>;
  skills: Skill[];
}

const skillCategories: SkillCategory[] = [
  {
    title: 'Languages',
    icon: Code2,
    skills: [
      { name: 'Python', level: 5, status: 'active' },
      { name: 'TypeScript', level: 5, status: 'active' },
      { name: 'JavaScript', level: 5, status: 'active' },
      { name: 'Rust', level: 3, status: 'experimenting' },
      { name: 'C++', level: 2, status: 'experimenting' },
      { name: 'SQL', level: 4, status: 'active' },
    ],
  },
  {
    title: 'Frameworks & Libs',
    icon: Database,
    skills: [
      { name: 'Next.js / React', level: 5, status: 'active' },
      { name: 'FastAPI / Flask', level: 5, status: 'active' },
      { name: 'Node.js / Express', level: 4, status: 'active' },
      { name: 'Tailwind CSS', level: 5, status: 'active' },
      { name: 'Textual (TUI)', level: 4, status: 'active' },
    ],
  },
  {
    title: 'AI & ML Integrations',
    icon: Cpu,
    skills: [
      { name: 'FastMCP / MCP spec', level: 5, status: 'active' },
      { name: 'LangChain / LlamaIndex', level: 4, status: 'active' },
      { name: 'Vector Databases (Chroma, PGVector)', level: 4, status: 'active' },
      { name: 'Hugging Face API', level: 3, status: 'active' },
      { name: 'Claude API / Code Agents', level: 5, status: 'active' },
    ],
  },
  {
    title: 'DevOps & Systems',
    icon: Wrench,
    skills: [
      { name: 'Docker / Compose', level: 4, status: 'active' },
      { name: 'GitHub Actions (CI/CD)', level: 4, status: 'active' },
      { name: 'Vercel / AWS', level: 4, status: 'active' },
      { name: 'Linux / Bash Scripting', level: 4, status: 'active' },
      { name: 'PyInstaller Bundling', level: 5, status: 'active' },
    ],
  },
  {
    title: 'Design & Drafting',
    icon: Palette,
    skills: [
      { name: 'Figma UI/UX', level: 4, status: 'active' },
      { name: 'Rhino 3D / Grasshopper', level: 5, status: 'active' },
      { name: 'AutoCAD Drafting', level: 4, status: 'active' },
      { name: 'Adobe Creative Suite', level: 4, status: 'active' },
    ],
  },
];

export default function SkillsCanvas() {
  const [activeCategory, setActiveCategory] = useState<number>(0);

  return (
    <section id="skills" className="border-b border-border bg-background py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 05 / CAPABILITIES
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
              Technical Competencies
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-xl">
              A comprehensive panel mapping language proficiencies, system framework familiarity, and computer-aided design capabilities.
            </p>
          </div>
        </div>

        {/* Blueprint Layout Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 border border-border rounded-xl bg-card/10 overflow-hidden shadow-md">
          
          {/* Categories Navigation Sidebar (Left Columns) */}
          <div className="lg:col-span-4 border-r border-border divide-y divide-border bg-card/30">
            {skillCategories.map((category, index) => {
              const Icon = category.icon;
              const isActive = activeCategory === index;
              
              return (
                <button
                  key={category.title}
                  onClick={() => setActiveCategory(index)}
                  className={`w-full flex items-center justify-between p-5 text-left font-mono text-xs font-semibold cursor-pointer transition-all ${
                    isActive
                      ? 'bg-primary/10 text-primary border-l-2 border-primary'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-4.5 w-4.5 ${isActive ? 'text-primary' : 'text-muted-foreground'}`} />
                    <span>{category.title}</span>
                  </div>
                  <span className="text-[10px] text-muted-foreground/60">
                    // 0{index + 1}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Active Skills List Panel (Right Columns) */}
          <div className="lg:col-span-8 p-6 sm:p-8 space-y-6 bg-card/10 relative">
            {/* Visual background details to resemble drafting grid */}
            <div className="absolute top-4 right-4 font-mono text-[9px] text-muted-foreground/40 uppercase">
              PANEL_REF: COMP_0{activeCategory + 1}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {skillCategories[activeCategory].skills.map((skill, index) => (
                <motion.div
                  key={skill.name}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="p-4 border border-border/80 bg-card rounded-lg flex flex-col justify-between hover:border-primary/30 transition-all"
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <span className="text-sm font-bold text-foreground">
                      {skill.name}
                    </span>
                    <span className={`px-2 py-0.5 rounded-[4px] text-[8px] font-mono border ${
                      skill.status === 'active'
                        ? 'border-emerald-500/20 text-emerald-400 bg-emerald-500/5'
                        : 'border-amber-500/20 text-amber-400 bg-amber-500/5'
                    }`}>
                      {skill.status}
                    </span>
                  </div>

                  {/* Subtle, non-gamified proficiency dots */}
                  <div className="flex items-center justify-between border-t border-border/50 pt-2">
                    <span className="font-mono text-[9px] text-muted-foreground uppercase">
                      PROFIENCY
                    </span>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((dot) => (
                        <div
                          key={dot}
                          className={`w-1.5 h-1.5 rounded-full ${
                            dot <= skill.level
                              ? 'bg-primary'
                              : 'bg-zinc-800'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Panel Footer Blueprint Note */}
            <div className="border-t border-border/60 pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[10px] font-mono text-muted-foreground">
              <span>ACTIVE: Daily Production Usage</span>
              <span>EXPERIMENTING: Side Projects &amp; R&amp;D</span>
            </div>

          </div>

        </div>
      </div>
    </section>
  );
}
