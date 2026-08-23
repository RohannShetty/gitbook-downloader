import React, { useState, useEffect } from "react"
import { Terminal, Download, Star, Menu, X, Check, Copy, Sparkles, ExternalLink } from "lucide-react"

interface HeaderProps {
  onOpenInstallModal: () => void
}

export const Header: React.FC<HeaderProps> = ({ onOpenInstallModal }) => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const copyQuickInstall = () => {
    navigator.clipboard.writeText("pip install gitbook-downloader")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const navLinks = [
    { name: "Frameworks", href: "#frameworks" },
    { name: "Output Contract", href: "#contract" },
    { name: "Export Studio", href: "#export-studio" },
    { name: "Feature Matrix", href: "#comparison" },
    { name: "FastMCP", href: "#mcp" },
    { name: "Personas", href: "#personas" },
    { name: "FAQ", href: "#faq" },
  ]

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[#09090b]/90 backdrop-blur-md border-b border-zinc-800/80 py-3 shadow-2xl shadow-black/40"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Brand Lockup */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-700/80 p-1.5 flex items-center justify-center transition-transform duration-300 group-hover:scale-105 group-hover:border-cyan-400/50 shadow-md">
            <svg viewBox="74 116 365 280" className="w-full h-full text-zinc-100" fill="none">
              <rect x="100" y="142" width="170" height="228" rx="30" stroke="#e4e4e7" strokeWidth="26" />
              <line x1="148" y1="214" x2="222" y2="214" stroke="#71717a" strokeWidth="20" strokeLinecap="round" />
              <line x1="148" y1="270" x2="222" y2="270" stroke="#71717a" strokeWidth="20" strokeLinecap="round" />
              <path d="M288 206 L344 256 L288 306" stroke="#00e5ff" strokeWidth="28" strokeLinecap="round" strokeLinejoin="round" />
              <line x1="374" y1="306" x2="412" y2="306" stroke="#00e5ff" strokeWidth="28" strokeLinecap="round" />
            </svg>
            <div className="absolute inset-0 rounded-xl bg-cyan-500/10 blur-sm group-hover:bg-cyan-500/20 transition-all" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-zinc-100 tracking-tight font-mono group-hover:text-cyan-300 transition-colors">
                DocHarvest
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-md">
                v10.0.0
              </span>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono hidden sm:inline-block">
              Universal Doc-to-Markdown Engine
            </span>
          </div>
        </a>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-6">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="text-xs font-medium text-zinc-300 hover:text-cyan-400 transition-colors py-1 relative group"
            >
              {link.name}
              <span className="absolute bottom-0 left-0 w-0 h-[2px] bg-gradient-to-r from-cyan-400 to-indigo-500 transition-all duration-200 group-hover:w-full" />
            </a>
          ))}
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Quick Install Pill */}
          <button
            onClick={copyQuickInstall}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/90 border border-zinc-700/80 text-xs font-mono text-zinc-300 hover:border-cyan-500/40 hover:text-zinc-100 transition-all group shadow-sm"
            title="Click to copy quick install command"
          >
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            <span>pip install gitbook-downloader</span>
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400 animate-in zoom-in" />
            ) : (
              <Copy className="w-3.5 h-3.5 text-zinc-500 group-hover:text-zinc-300" />
            )}
          </button>

          {/* GitHub Star Button */}
          <a
            href="https://github.com/RohannShetty/gitbook-downloader"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-300 hover:text-white hover:border-zinc-700 transition-all"
          >
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/20" />
            <span>Star</span>
            <span className="ml-1 px-1.5 py-0.2 text-[11px] bg-zinc-800 rounded text-zinc-400 font-mono">
              GitHub
            </span>
          </a>

          {/* Download CTA */}
          <button
            onClick={onOpenInstallModal}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-zinc-950 font-semibold text-xs transition-all shadow-md shadow-cyan-500/10 hover:shadow-cyan-500/20 hover:scale-[1.02] active:scale-[0.98]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Get Started</span>
          </button>
        </div>

        {/* Mobile Menu Toggle */}
        <div className="flex sm:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="sm:hidden bg-[#09090b] border-b border-zinc-800 px-6 py-5 mt-3 space-y-4 shadow-xl">
          <div className="grid grid-cols-2 gap-2">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className="text-sm font-medium text-zinc-300 hover:text-cyan-400 py-1.5"
              >
                {link.name}
              </a>
            ))}
          </div>
          <div className="pt-3 border-t border-zinc-800 flex flex-col gap-2">
            <button
              onClick={() => {
                copyQuickInstall()
                setMobileMenuOpen(false)
              }}
              className="flex items-center justify-center gap-2 w-full py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-xs font-mono text-zinc-300"
            >
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>{copied ? "Copied to Clipboard!" : "Copy Install Command"}</span>
            </button>
            <button
              onClick={() => {
                onOpenInstallModal()
                setMobileMenuOpen(false)
              }}
              className="flex items-center justify-center gap-2 w-full py-2 bg-gradient-to-r from-cyan-500 to-indigo-600 text-zinc-950 font-semibold rounded-lg text-xs"
            >
              <Download className="w-4 h-4" />
              <span>Download DocHarvest</span>
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
