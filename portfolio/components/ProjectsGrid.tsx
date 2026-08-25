'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowUpRight, Code, Compass, Hammer, Cpu, Terminal } from 'lucide-react';
import { GithubIcon } from './Icons';
import { ProjectMetadata } from '@/lib/mdx';

interface ProjectsGridProps {
  projects: ProjectMetadata[];
}

// Icon mappings based on project categories to provide visual structure
const categoryIcons: Record<string, React.ComponentType<any>> = {
  'System Infrastructure': Cpu,
  'Developer Automation': Hammer,
  'AI Tooling': Terminal,
  'Productivity Tools': Compass,
  'Developer Tooling': Code,
};

export default function ProjectsGrid({ projects }: ProjectsGridProps) {
  return (
    <section id="projects" className="border-b border-border bg-background py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 02 / SELECTED WORK
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
              Production-Grade Projects
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-xl">
              Case studies detailing core system designs, automation daemons, and compiler scraping tools.
            </p>
          </div>
          <div className="font-mono text-[10px] text-muted-foreground">
            TOTAL_INDEXED_REPOS: {projects.length}
          </div>
        </div>

        {/* Flat Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, index) => {
            const IconComponent = categoryIcons[project.category] || Code;
            
            return (
              <motion.div
                key={project.slug}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                className="group flex flex-col justify-between border border-border bg-card rounded-xl p-6 hover:border-primary/50 hover:shadow-lg transition-all duration-300 relative overflow-hidden"
              >
                {/* Structural corner marks */}
                <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-border group-hover:border-primary transition-colors" />
                <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-border group-hover:border-primary transition-colors" />
                <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-border group-hover:border-primary transition-colors" />
                <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-border group-hover:border-primary transition-colors" />

                <div className="space-y-4">
                  {/* Category Header */}
                  <div className="flex items-center justify-between border-b border-border/80 pb-3">
                    <div className="flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground uppercase">
                      <IconComponent className="h-3.5 w-3.5 text-primary" />
                      <span>{project.category}</span>
                    </div>
                    {project.githubUrl && (
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-secondary transition-all"
                        title="GitHub Repository"
                      >
                        <GithubIcon className="h-4 w-4" />
                      </a>
                    )}
                  </div>

                  {/* Title & Description */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
                      {project.title}
                    </h3>
                    <p className="text-xs text-muted-foreground font-mono leading-relaxed line-clamp-3">
                      {project.description}
                    </p>
                  </div>
                </div>

                <div className="space-y-4 pt-4 mt-auto">
                  {/* Tech stack tags */}
                  <div className="flex flex-wrap gap-1.5">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary/35 text-muted-foreground"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Footer CTAs */}
                  <div className="flex items-center justify-between pt-3 border-t border-border/50">
                    <Link
                      href={`/projects/${project.slug}`}
                      className="inline-flex items-center gap-1 text-xs font-mono font-semibold text-foreground hover:text-primary transition-colors group/link"
                    >
                      <span>Read Case Study</span>
                      <ArrowUpRight className="h-3.5 w-3.5 group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                    </Link>

                    {project.demoUrl && (
                      <a
                        href={project.demoUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] font-mono text-muted-foreground hover:text-accent transition-colors"
                      >
                        Live Demo
                      </a>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
