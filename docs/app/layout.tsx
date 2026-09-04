import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/ThemeProvider";
import { VERSION } from "../lib/version";
import { FAQ_ITEMS } from "../data/showcaseData";
import "./globals.css";

const geistSans = Geist({
  variable: "--geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist({
  variable: "--geist-mono",
  subsets: ["latin"],
});

const SITE_URL = "https://rohannshetty.github.io";
const SITE_PATH = "/gitbook-downloader/";

// Rich-result structured data: SoftwareApplication + FAQPage (mirrors the visible FAQ).
const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      name: "DocHarvest",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Windows, Linux, macOS",
      softwareVersion: VERSION,
      url: `${SITE_URL}${SITE_PATH}`,
      description:
        "Local-first documentation compiler: turns any doc site into LLM-ready Markdown, RAG JSONL, llms.txt & offline PDFs. FastMCP server for Cursor, Claude Code & 14 clients. 100% local, MIT.",
      license: "https://opensource.org/licenses/MIT",
      author: {
        "@type": "Person",
        name: "Rohan Shetty",
        url: "https://github.com/RohannShetty",
      },
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
      featureList: [
        "8 documentation platform auto-detectors with direct .md endpoint probing",
        "Four-Part Output Contract: pages/, book.md, llms.txt, search index",
        "RAG JSONL export with SHA-256 frontmatter provenance",
        "Pure-Python PDF handbooks (fpdf2, zero C-dependencies)",
        "Embedded SQLite FTS5 BM25 search",
        "FastMCP v2 server with 12 tools for AI coding agents",
      ],
    },
    {
      "@type": "FAQPage",
      mainEntity: FAQ_ITEMS.map((f) => ({
        "@type": "Question",
        name: f.q,
        acceptedAnswer: { "@type": "Answer", text: f.a },
      })),
    },
  ],
};

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "DocHarvest — Documentation Compiler for LLMs, RAG & MCP",
  description:
    "Stop burning context tokens on cookie banners. DocHarvest compiles any doc portal into LLM-ready Markdown, RAG JSONL, llms.txt & offline PDFs — 100% local, MIT, FastMCP included.",
  alternates: { canonical: SITE_PATH },
  keywords: [
    // Discovery layer — high-intent queries users actually type (metadata only,
    // never used in on-page self-description; see docs/SEO_GUIDE.md §2)
    "documentation scraper",
    "mintlify scraper",
    "gitbook downloader",
    // Positioning layer — what the product is
    "documentation compiler",
    "documentation harvester",
    "llm-ready markdown",
    "llm context",
    "rag dataset generator",
    "llms.txt",
    "mcp server",
    "fastmcp",
    "docusaurus offline",
    "offline documentation",
    "pdf generator",
    "ai coding agent docs",
  ],
  authors: [{ name: "Rohan Shetty", url: "https://github.com/RohannShetty" }],
  openGraph: {
    title: "DocHarvest — Documentation Compiler for LLMs, RAG & MCP",
    description:
      "Stop burning context tokens on cookie banners. Turn any doc portal into clean LLM context, RAG datasets & offline PDFs — 100% local, free & open source.",
    url: SITE_PATH,
    siteName: "DocHarvest",
    type: "website",
    images: [
      {
        url: `${SITE_PATH}assets/og-capture-studio.png`,
        width: 1024,
        height: 576,
        alt: "DocHarvest desktop GUI capturing a documentation site",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "DocHarvest — Documentation Compiler for LLMs, RAG & MCP",
    description:
      "Turn any doc site into clean LLM context, RAG JSONL & offline PDFs. 100% local, MIT, FastMCP included.",
    creator: "@rohan__shetty",
    images: [`${SITE_PATH}assets/og-capture-studio.png`],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script
          async
          src="https://startupbar.co/widget/loader.js"
          data-startup-id="6e9a63c4-5bc5-4b8b-b297-37a9450c7f1f"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                var saved = localStorage.getItem('theme');
                if (saved === 'light') {
                  document.documentElement.classList.add('light');
                } else {
                  document.documentElement.classList.remove('light');
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground transition-colors duration-300">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
