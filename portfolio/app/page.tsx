import React from 'react';
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import About from '@/components/About';
import ProjectsGrid from '@/components/ProjectsGrid';
import SkillsCanvas from '@/components/SkillsCanvas';
import BlogList from '@/components/BlogList';
import GithubFeed from '@/components/GithubFeed';
import Footer from '@/components/Footer';
import { getProjects } from '@/lib/mdx';
import { getBlogPosts } from '@/lib/mdx';
import { getGithubData } from '@/lib/github';

// Revalidate page cache every hour
export const revalidate = 3600;

export default async function Home() {
  // Fetch MDX metadata
  const projects = getProjects();
  const blogPosts = getBlogPosts();
  
  // Fetch GitHub Activity metrics
  const githubData = await getGithubData('rohannshetty');

  return (
    <div className="flex flex-col min-h-screen">
      {/* Premium Header */}
      <Navbar />

      {/* Main Showcase Layout */}
      <main className="flex-1">
        {/* Hero Banner */}
        <Hero />
        
        {/* Profile Biography */}
        <About />
        
        {/* Project Case Studies */}
        <ProjectsGrid projects={projects} />
        
        {/* Competencies Panel */}
        <SkillsCanvas />
        
        {/* Blog / Technical Writing */}
        <BlogList posts={blogPosts} />
        
        {/* Real-time GitHub Activity Feed */}
        <GithubFeed 
          profile={githubData.profile}
          repos={githubData.repos}
          commits={githubData.commits}
        />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
