import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Globe, Calendar, Tag } from 'lucide-react';
import { GithubIcon } from '@/components/Icons';
import { getProjectBySlug, getProjects } from '@/lib/mdx';
import { MDXRemote } from 'next-mdx-remote/rsc';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface ProjectPageProps {
  params: Promise<{
    slug: string;
  }>;
}

export async function generateStaticParams() {
  const projects = getProjects();
  return projects.map((project) => ({
    slug: project.slug,
  }));
}

export default async function ProjectPage({ params }: ProjectPageProps) {
  const { slug } = await params;
  const project = getProjectBySlug(slug);

  if (!project) {
    notFound();
  }

  const { metadata, body } = project;

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 py-12 bg-background">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          
          {/* Back button */}
          <Link
            href="/#projects"
            className="inline-flex items-center gap-2 text-xs font-mono text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Work</span>
          </Link>

          {/* Project Header Board */}
          <div className="border border-border rounded-xl bg-card p-6 sm:p-8 mb-10 relative overflow-hidden">
            {/* Architectural draft marks */}
            <div className="absolute top-2 left-2 font-mono text-[9px] text-muted-foreground/40">REF: CASE_STUDY_{slug.toUpperCase()}</div>
            
            <div className="space-y-4">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono border border-border bg-secondary text-primary font-bold uppercase tracking-wide">
                {metadata.category}
              </span>
              
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
                {metadata.title}
              </h1>
              
              <p className="text-sm text-muted-foreground font-mono leading-relaxed max-w-2xl">
                {metadata.description}
              </p>

              {/* Tag links and resources */}
              <div className="flex flex-wrap items-center justify-between gap-4 pt-6 border-t border-border/80">
                <div className="flex flex-wrap gap-1.5">
                  {metadata.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary/35 text-muted-foreground"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-3">
                  {metadata.githubUrl && (
                    <a
                      href={metadata.githubUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-mono text-muted-foreground hover:text-foreground border border-border bg-background px-3 py-1.5 rounded-lg transition-all"
                    >
                      <GithubIcon className="w-3.5 h-3.5" />
                      <span>Codebase</span>
                    </a>
                  )}
                  {metadata.demoUrl && (
                    <a
                      href={metadata.demoUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-mono text-muted-foreground hover:text-accent border border-border bg-background px-3 py-1.5 rounded-lg transition-all"
                    >
                      <Globe className="w-3.5 h-3.5 text-accent" />
                      <span>Live Demo</span>
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Case Study Content (MDX Dynamic Compilation) */}
          <article className="prose prose-zinc dark:prose-invert max-w-none font-mono text-sm leading-relaxed text-muted-foreground space-y-6 
            prose-headings:text-foreground prose-headings:font-bold prose-headings:tracking-tight prose-headings:font-sans
            prose-h2:text-xl prose-h2:border-b prose-h2:border-border prose-h2:pb-2 prose-h2:pt-4
            prose-h3:text-base prose-h3:font-semibold
            prose-strong:text-foreground
            prose-a:text-primary prose-a:no-underline hover:prose-a:underline"
          >
            <MDXRemote source={body} />
          </article>

        </div>
      </main>

      <Footer />
    </div>
  );
}
