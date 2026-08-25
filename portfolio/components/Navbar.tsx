'use client';

import React from 'react';
import Link from 'next/link';
import { useTheme } from './ThemeProvider';
import { Sun, Moon, ArrowRight } from 'lucide-react';
import { GithubIcon, LinkedinIcon } from './Icons';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo/Identity */}
        <Link href="/" className="group flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground font-mono font-bold text-lg shadow-md group-hover:scale-105 transition-transform duration-200">
            R
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-sm font-bold tracking-tight text-foreground">
              Rohan Shetty
            </span>
            <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-wider">
              Arch + Dev
            </span>
          </div>
        </Link>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-8 font-mono text-xs font-medium text-muted-foreground">
          <Link href="#about" className="hover:text-foreground transition-colors">
            // about
          </Link>
          <Link href="#projects" className="hover:text-foreground transition-colors">
            // projects
          </Link>
          <Link href="#skills" className="hover:text-foreground transition-colors">
            // skills
          </Link>
          <Link href="#blog" className="hover:text-foreground transition-colors">
            // blog
          </Link>
          <Link href="#github" className="hover:text-foreground transition-colors">
            // git-activity
          </Link>
        </nav>

        {/* Action controls */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 border-r border-border pr-4">
            <a
              href="https://github.com/rohannshetty"
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-all duration-200"
              title="GitHub Profile"
            >
              <GithubIcon className="h-4 w-4" />
            </a>
            <a
              href="https://linkedin.com/in/rohannshetty"
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-all duration-200"
              title="LinkedIn Profile"
            >
              <LinkedinIcon className="h-4 w-4" />
            </a>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg border border-border bg-secondary/50 text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all duration-200 cursor-pointer"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-500" /> : <Moon className="h-4 w-4 text-indigo-500" />}
          </button>

          {/* Contact Button */}
          <Link
            href="mailto:shettyrohan2@gmail.com"
            className="inline-flex h-9 items-center justify-center rounded-lg bg-primary px-4 text-xs font-mono font-bold text-primary-foreground hover:bg-primary/95 shadow-sm transition-all duration-200"
          >
            Contact
          </Link>
        </div>
      </div>
    </header>
  );
}
