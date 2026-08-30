'use client';

import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Download, Terminal, Layers } from 'lucide-react';
import { WindowsIcon, LinuxIcon, AppleIcon, PythonIcon, DockerIcon } from './Icons';
import { VERSION, DOWNLOAD_URLS } from '../lib/version';

interface InstallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const INSTALL_OPTIONS = [
  {
    id: "windows",
    title: "Windows Standalone",
    icon: WindowsIcon,
    command: "# Direct executable (zero Python install needed)\ncurl -LO " + DOWNLOAD_URLS.windows + "\n.\\docharvest-windows-latest.exe --gui",
    ctaUrl: DOWNLOAD_URLS.windows,
    ctaLabel: "Download docharvest.exe (32.9MB)"
  },
  {
    id: "pip",
    title: "pip / PyPI",
    icon: PythonIcon,
    command: "pip install gitbook-downloader\n\n# Run GUI:\ndocharvest --gui\n\n# Or CLI crawl:\ndocharvest crawl https://docs.openalgo.in/v/v2.0 --rag --pdf",
    ctaUrl: "https://pypi.org/project/gitbook-downloader/",
    ctaLabel: "View on PyPI"
  },
  {
    id: "uv",
    title: "uv / uvx (Ultra-Fast)",
    icon: Terminal,
    command: "# Run instantly with uv without installing to global Python:\nuvx gitbook-downloader --gui\n\n# Or install permanently:\nuv tool install gitbook-downloader",
    ctaUrl: "https://github.com/RohannShetty/gitbook-downloader",
    ctaLabel: "View GitHub Repo"
  },
  {
    id: "docker",
    title: "Docker Container",
    icon: DockerIcon,
    command: "# Run headless crawling daemon:\ndocker run --rm -v $(pwd)/data:/app/data rohanshetty/docharvest crawl https://docs.openalgo.in",
    ctaUrl: "https://github.com/RohannShetty/gitbook-downloader",
    ctaLabel: "View Dockerfile"
  }
];

export function InstallModal({ isOpen, onClose }: InstallModalProps) {
  const [activeTab, setActiveTab] = useState(INSTALL_OPTIONS[0]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeTab.command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div
        className="relative w-full max-w-2xl border border-border rounded-xl bg-card text-foreground shadow-2xl p-6 sm:p-8 space-y-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/80 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/30">
              <Download className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">
                Install DocHarvest v{VERSION}
              </h3>
              <p className="text-xs text-muted-foreground font-mono">
                Select your operating system or preferred package manager.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Selection */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {INSTALL_OPTIONS.map((opt) => {
            const isSelected = activeTab.id === opt.id;
            const Icon = opt.icon;
            return (
              <button
                key={opt.id}
                onClick={() => setActiveTab(opt)}
                className={`p-3 rounded-lg border font-mono text-xs font-semibold flex flex-col items-center gap-1.5 transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-primary ${
                  isSelected
                    ? 'border-primary bg-primary/15 text-primary'
                    : 'border-border bg-card text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="truncate">{opt.title.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>

        {/* Command Box */}
        <div className="space-y-2">
          <div className="flex items-center justify-between font-mono text-[11px] text-muted-foreground">
            <span>Terminal Command:</span>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-cyan font-bold hover:underline cursor-pointer focus-visible:outline-2 focus-visible:outline-primary"
              aria-label="Copy install command"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-cyan/50" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy'}</span>
            </button>
          </div>

          <div className="p-4 rounded-lg bg-card/95 border border-border/80 font-mono text-xs text-cyan/90 leading-relaxed overflow-x-auto shadow-inner">
            <pre className="!bg-transparent !p-0 !border-0 text-cyan/90">
              <code>{activeTab.command}</code>
            </pre>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-2">
          <a
            href={activeTab.ctaUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-5 font-mono text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-md shadow-primary/20"
          >
            <Download className="h-4 w-4" />
            <span>{activeTab.ctaLabel}</span>
          </a>

          <button
            onClick={onClose}
            className="h-10 px-4 rounded-lg border border-border bg-secondary/50 font-mono text-xs text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors cursor-pointer focus-visible:outline-2 focus-visible:outline-primary"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
