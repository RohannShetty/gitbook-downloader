import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Calendar, Tag, User } from 'lucide-react';
import { getBlogPostBySlug, getBlogPosts } from '@/lib/mdx';
import { MDXRemote } from 'next-mdx-remote/rsc';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface BlogPageProps {
  params: Promise<{
    slug: string;
  }>;
}

export async function generateStaticParams() {
  const posts = getBlogPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export default async function BlogPostPage({ params }: BlogPageProps) {
  const { slug } = await params;
  const post = getBlogPostBySlug(slug);

  if (!post) {
    notFound();
  }

  const { metadata, body } = post;

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 py-12 bg-background">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          
          {/* Back button */}
          <Link
            href="/#blog"
            className="inline-flex items-center gap-2 text-xs font-mono text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Writing</span>
          </Link>

          {/* Post Header */}
          <div className="space-y-4 mb-10 pb-8 border-b border-border">
            <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3 text-primary" />
                {metadata.date}
              </span>
              <span>•</span>
              <span className="px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary text-primary font-bold uppercase tracking-wide">
                {metadata.category}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                Rohan Shetty
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground leading-tight">
              {metadata.title}
            </h1>

            <p className="text-sm text-muted-foreground font-mono leading-relaxed italic">
              {metadata.description}
            </p>

            <div className="flex flex-wrap gap-1.5 pt-2">
              {metadata.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary/35 text-muted-foreground"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>

          {/* Post Body (MDX Dynamic Compilation) */}
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
