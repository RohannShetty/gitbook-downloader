import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/ThemeProvider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DocHarvest — The Universal Documentation Harvester for LLMs, RAG & Offline Books",
  description: "Turn any documentation portal (GitBook, Mintlify, Docusaurus, Nextra, ReadMe, VitePress, MkDocs) into clean LLM-ready Markdown, vector RAG JSONL datasets, llms.txt manifests, and publication-grade offline PDFs. Zero-config CLI, desktop GUI & FastMCP server.",
  keywords: [
    "documentation scraper",
    "rag dataset generator",
    "llms.txt",
    "gitbook downloader",
    "mintlify scraper",
    "docusaurus offline",
    "mcp server",
    "fastmcp",
    "offline documentation",
    "pdf generator"
  ],
  authors: [{ name: "Rohan Shetty", url: "https://github.com/RohannShetty" }],
  openGraph: {
    title: "DocHarvest — Turn Any Docs into LLM-Ready Markdown & RAG Datasets",
    description: "The universal documentation scraper, RAG vector compiler, and offline PDF handbook generator for AI coding agents.",
    url: "https://rohannshetty.github.io/gitbook-downloader/",
    siteName: "DocHarvest",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "DocHarvest — Turn Any Docs into LLM-Ready Markdown & RAG Datasets",
    description: "Universal documentation harvester for GitBook, Mintlify, Docusaurus, Nextra, and ReadMe. FastMCP server included.",
    creator: "@rohannshetty",
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
