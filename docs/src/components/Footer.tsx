import React from "react"
import { Terminal, Github, Star, Heart, ArrowUp, ExternalLink } from "lucide-react"

export const Footer: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  return (
    <footer className="bg-[#070709] border-t border-zinc-800/80 pt-16 pb-12 text-zinc-400 text-xs font-mono relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 pb-12 border-b border-zinc-800/80">
          {/* Brand Column */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-700 p-1 flex items-center justify-center">
                <svg viewBox="74 116 365 280" className="w-full h-full text-zinc-100" fill="none">
                  <rect x="100" y="142" width="170" height="228" rx="30" stroke="#e4e4e7" strokeWidth="26" />
                  <line x1="148" y1="214" x2="222" y2="214" stroke="#71717a" strokeWidth="20" strokeLinecap="round" />
                  <line x1="148" y1="270" x2="222" y2="270" stroke="#71717a" strokeWidth="20" strokeLinecap="round" />
                  <path d="M288 206 L344 256 L288 306" stroke="#00e5ff" strokeWidth="28" strokeLinecap="round" strokeLinejoin="round" />
                  <line x1="374" y1="306" x2="412" y2="306" stroke="#00e5ff" strokeWidth="28" strokeLinecap="round" />
                </svg>
              </div>
              <span className="font-bold text-base text-white tracking-tight font-sans">DocHarvest</span>
            </div>
            <p className="text-zinc-400 text-xs leading-relaxed font-sans">
              Turn any documentation site into clean, LLM-ready Markdown, vector context &amp; offline books.
            </p>
            <div className="text-[11px] text-zinc-400">
              MIT Licensed • 100% Free &amp; Open Source
            </div>
          </div>

          {/* Product Links */}
          <div className="space-y-3">
            <div className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">Product</div>
            <ul className="space-y-2">
              <li>
                <a href="#frameworks" className="hover:text-cyan-400 transition-colors">
                  Supported Frameworks
                </a>
              </li>
              <li>
                <a href="#contract" className="hover:text-cyan-400 transition-colors">
                  Four-Part Output Contract
                </a>
              </li>
              <li>
                <a href="#export-studio" className="hover:text-cyan-400 transition-colors">
                  Multi-Target Export Studio
                </a>
              </li>
              <li>
                <a href="#comparison" className="hover:text-cyan-400 transition-colors">
                  Honest Capability Matrix
                </a>
              </li>
              <li>
                <a href="#mcp" className="hover:text-cyan-400 transition-colors">
                  FastMCP AI Agent Server
                </a>
              </li>
            </ul>
          </div>

          {/* Developer Ecosystem */}
          <div className="space-y-3">
            <div className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">Ecosystem</div>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-cyan-400 transition-colors flex items-center gap-1"
                >
                  <span>GitHub Repository</span>
                  <ExternalLink className="w-3 h-3 text-zinc-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://pypi.org/project/gitbook-downloader/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-cyan-400 transition-colors flex items-center gap-1"
                >
                  <span>PyPI Package</span>
                  <ExternalLink className="w-3 h-3 text-zinc-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/releases"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-cyan-400 transition-colors flex items-center gap-1"
                >
                  <span>Desktop GUI Releases</span>
                  <ExternalLink className="w-3 h-3 text-zinc-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/RohannShetty/gitbook-downloader/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-cyan-400 transition-colors flex items-center gap-1"
                >
                  <span>Issue Tracker &amp; Feedback</span>
                  <ExternalLink className="w-3 h-3 text-zinc-400" />
                </a>
              </li>
            </ul>
          </div>

          {/* Community & Quick Actions */}
          <div className="space-y-3">
            <div className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">Community</div>
            <p className="text-zinc-400 text-xs leading-relaxed font-sans">
              Star the project on GitHub to support open-source AI tooling and offline knowledge preservation.
            </p>
            <a
              href="https://github.com/RohannShetty/gitbook-downloader"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-700 text-xs font-semibold text-white hover:border-cyan-400/60 transition-all shadow-sm"
            >
              <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
              <span>Star on GitHub</span>
            </a>
          </div>
        </div>

        {/* Bottom Attribution & Back-to-Top */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-zinc-400">
          <div className="flex items-center gap-1.5 font-sans">
            <span>Authored with pride by Rohan Shetty &amp; the DocHarvest Contributors.</span>
          </div>

          <button
            onClick={scrollToTop}
            className="flex items-center gap-1.5 text-zinc-400 hover:text-cyan-400 transition-colors"
          >
            <span>Back to top</span>
            <ArrowUp className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </footer>
  )
}
