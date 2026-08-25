'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Calendar, Tag, ArrowRight } from 'lucide-react';
import { BlogMetadata } from '@/lib/mdx';

interface BlogListProps {
  posts: BlogMetadata[];
}

export default function BlogList({ posts }: BlogListProps) {
  return (
    <section id="blog" className="border-b border-border bg-background/50 py-20 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div className="space-y-3">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              // 03 / WRITING
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
              Technical Logs &amp; Writing
            </h2>
            <p className="text-sm text-muted-foreground font-mono max-w-xl">
              Thoughts on systems engineering, terminal developer tools, spatial design, and local AI agent tooling.
            </p>
          </div>
          <div className="font-mono text-[10px] text-muted-foreground">
            POSTS_PUBLISHED: {posts.length}
          </div>
        </div>

        {/* List Layout */}
        <div className="space-y-4">
          {posts.map((post, index) => (
            <motion.div
              key={post.slug}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
            >
              <Link
                href={`/blog/${post.slug}`}
                className="group flex flex-col md:flex-row md:items-center justify-between border border-border bg-card rounded-xl p-5 hover:border-primary/50 transition-all duration-200"
              >
                <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-8 flex-1">
                  {/* Date & Category Metadata */}
                  <div className="flex items-center gap-3 font-mono text-[10px] text-muted-foreground shrink-0 md:w-32">
                    <Calendar className="h-3.5 w-3.5 text-primary" />
                    <span>{post.date}</span>
                  </div>

                  {/* Post Title & Description */}
                  <div className="space-y-1.5 flex-1 min-w-0 pr-4">
                    <h3 className="text-base font-bold tracking-tight text-foreground group-hover:text-primary transition-colors truncate">
                      {post.title}
                    </h3>
                    <p className="text-xs text-muted-foreground font-mono truncate">
                      {post.description}
                    </p>
                  </div>
                </div>

                {/* Categories & Actions */}
                <div className="flex items-center gap-4 mt-4 md:mt-0 justify-between md:justify-end shrink-0">
                  <div className="flex items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary text-primary font-semibold uppercase">
                      {post.category}
                    </span>
                    {post.tags.slice(0, 1).map(tag => (
                      <span key={tag} className="hidden sm:inline-flex px-2 py-0.5 rounded text-[9px] font-mono border border-border bg-secondary/35 text-muted-foreground">
                        #{tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center justify-center h-7 w-7 rounded-lg border border-border bg-background group-hover:border-primary/50 group-hover:text-primary transition-all">
                    <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
