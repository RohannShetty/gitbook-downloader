import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { InstallModal } from '@/components/InstallModal';
import { McpShowcase } from '@/components/McpShowcase';
import { AgentEcosystemShowcase } from '@/components/AgentEcosystemShowcase';
import { ExportStudioPreview } from '@/components/ExportStudioPreview';
import { GithubReleaseFeed } from '@/components/GithubReleaseFeed';
import { ThemeProvider } from '@/components/ThemeProvider';

import type { DocHarvestGithubData } from '@/lib/github';

// Mock next/link to avoid needing Next.js router context
vi.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) =>
    React.createElement('a', props, children),
}));

const noop = vi.fn();

// --- Mock data for GithubReleaseFeed ---
const mockGithubData: DocHarvestGithubData = {
  stats: {
    stars: 128,
    forks: 16,
    openIssues: 0,
    watchers: 128,
    updatedAt: '2026-08-30T00:00:00Z',
  },
  latestRelease: {
    tag: 'v11.0.3',
    name: 'DocHarvest v11.0.3',
    publishedAt: '2026-08-30',
    body: 'Test release body',
    htmlUrl: 'https://github.com/RohannShetty/gitbook-downloader/releases/tag/v11.0.3',
    assets: [
      {
        name: 'docharvest-windows-latest.exe',
        size: 34500000,
        downloadCount: 520,
      browserDownloadUrl: 'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.3/docharvest-windows-latest.exe',
        os: 'windows',
      },
      {
        name: 'docharvest-linux-x86_64',
        size: 48300000,
        downloadCount: 210,
      browserDownloadUrl: 'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.3/docharvest-ubuntu-latest',
        os: 'linux',
      },
      {
        name: 'docharvest-macos-universal',
        size: 30400000,
        downloadCount: 290,
      browserDownloadUrl: 'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.3/docharvest-macos-latest',
        os: 'macos',
      },
    ],
  },
  recentCommits: [
    {
      sha: '8c61e9e',
      message: 'chore: release v11.0.3',
      date: '2026-08-23',
      author: 'Rohan Shetty',
      url: 'https://github.com/RohannShetty/gitbook-downloader/commit/8c61e9e',
    },
    {
      sha: 'f1e2d3c',
      message: 'feat: add FastMCP server',
      date: '2026-08-22',
      author: 'Rohan Shetty',
      url: 'https://github.com/RohannShetty/gitbook-downloader/commit/f1e2d3c',
    },
  ],
};

// --- Helper: find button by visible span text ---
function findButtonByText(text: string): HTMLButtonElement {
  const span = screen.getByText(text, { selector: 'span' });
  const button = span.closest('button');
  if (!button) throw new Error(`Button not found for text "${text}"`);
  return button;
}

// --- Header ---
describe('Header aria-labels', () => {
  it('theme toggle button has aria-label', () => {
    render(
      <ThemeProvider>
        <Header onOpenInstallModal={noop} />
      </ThemeProvider>
    );
    // Default theme is 'dark' so title reads "Switch to Light Mode"
    const themeButton = screen.getByTitle('Switch to Light Mode');
    expect(themeButton).toHaveAttribute('aria-label', 'Switch to Light Mode');
  });
});

// --- Hero ---
describe('Hero aria-labels', () => {
  it('copy pip install command button has aria-label', () => {
    render(<Hero onOpenInstallModal={noop} />);
    const copyButton = findButtonByText('Copy');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy pip install command');
  });
});

// --- InstallModal ---
describe('InstallModal aria-labels', () => {
  it('close (X) button has aria-label', () => {
    render(<InstallModal isOpen={true} onClose={noop} />);
    // Find icon-only button (no text content)
    const buttons = screen.getAllByRole('button');
    const iconOnlyButton = buttons.find(b => !b.textContent?.trim());
    expect(iconOnlyButton).toHaveAttribute('aria-label', 'Close');
  });

  it('copy command button has aria-label', () => {
    render(<InstallModal isOpen={true} onClose={noop} />);
    const copyButton = findButtonByText('Copy');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy install command');
  });
});

// --- McpShowcase ---
describe('McpShowcase aria-labels', () => {
  it('copy configuration button has aria-label', () => {
    render(<McpShowcase />);
    const copyButton = findButtonByText('Copy JSON');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy MCP configuration');
  });
});

// --- AgentEcosystemShowcase ---
describe('AgentEcosystemShowcase aria-labels', () => {
  it('copy config button has aria-label', () => {
    render(<AgentEcosystemShowcase />);
    const copyButton = findButtonByText('Copy FastMCP JSON');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy FastMCP configuration');
  });

  it('copy CLI command button has aria-label', () => {
    render(<AgentEcosystemShowcase />);
    const copyButton = findButtonByText('Copy CLI');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy CLI command');
  });
});

// --- ExportStudioPreview ---
describe('ExportStudioPreview aria-labels', () => {
  it('copy sample code button has aria-label', () => {
    render(<ExportStudioPreview />);
    const copyButton = findButtonByText('Copy Sample');
    expect(copyButton).toHaveAttribute('aria-label', 'Copy sample code');
  });
});

// --- GithubReleaseFeed ---
describe('GithubReleaseFeed aria-labels', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false } as any));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('copy commit hash buttons have aria-label', async () => {
    render(<GithubReleaseFeed data={mockGithubData} />);
    // Flush async useEffect (mocked fetch resolves immediately)
    await new Promise(resolve => setTimeout(resolve, 0));
    const shaButtons = screen.getAllByTitle('Click to copy commit hash');
    expect(shaButtons.length).toBeGreaterThan(0);
    shaButtons.forEach(btn => {
      expect(btn).toHaveAttribute('aria-label', 'Copy commit hash');
    });
  });

  it('copy SHA-256 verification command button has aria-label', async () => {
    render(<GithubReleaseFeed data={mockGithubData} />);
    // Flush async useEffect (mocked fetch resolves immediately)
    await new Promise(resolve => setTimeout(resolve, 0));
    const verifyButton = screen.getByTitle('Copy PowerShell verification command');
    expect(verifyButton).toHaveAttribute('aria-label', 'Copy SHA-256 verification command');
  });
});
