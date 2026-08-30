import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import React from 'react';

// Mock next/link to avoid Next.js router dependency
vi.mock('next/link', () => ({
  default: ({ children, ...props }: Record<string, unknown>) =>
    React.createElement('a', props, children),
  __esModule: true,
}));

// Import all components under audit
import { AgentEcosystemShowcase } from '../AgentEcosystemShowcase';
import { DocTypeSelector } from '../DocTypeSelector';
import { ExportStudioPreview } from '../ExportStudioPreview';
import { FaqSection } from '../FaqSection';
import { Footer } from '../Footer';
import { GithubReleaseFeed } from '../GithubReleaseFeed';
import { Header } from '../Header';
import { Hero } from '../Hero';
import { InstallModal } from '../InstallModal';
import { McpShowcase } from '../McpShowcase';
import { OutputContract } from '../OutputContract';
import { ThemeProvider } from '../ThemeProvider';
import type { DocHarvestGithubData } from '../lib/github';

/**
 * Helper: find every <button> with cursor-pointer in the rendered output
 * and assert it also carries focus-visible:outline-2 and
 * focus-visible:outline-primary.
 */
function verifyFocusVisibleButtons(
  container: HTMLElement,
  componentName: string,
): void {
  const buttons = container.querySelectorAll('button, a[href]');
  let cursorButtons = 0;

  buttons.forEach((btn, idx) => {
    const cls = btn.getAttribute('class') || '';
    if (!cls.includes('cursor-pointer')) return;

    cursorButtons++;

    expect(cls, `${componentName}: button[${idx}] has cursor-pointer but is missing focus-visible:outline-2`)
      .toContain('focus-visible:outline-2');
    expect(cls, `${componentName}: button[${idx}] has cursor-pointer but is missing focus-visible:outline-primary`)
      .toContain('focus-visible:outline-primary');
  });

  expect(cursorButtons).toBeGreaterThan(
    0,
    `${componentName}: expected at least one button with cursor-pointer to verify — guard against false positives`,
  );
}

// Minimal mock data for GithubReleaseFeed
const mockGithubData = {
  stats: {
    stars: 128,
    forks: 50,
    openIssues: 3,
    watchers: 10,
    updatedAt: '2026-08-30',
  },
  latestRelease: {
    tag: 'v11.0.1',
    name: 'v11.0.1',
    publishedAt: '2026-08-23',
    body: '## What’s Changed\nSome changes',
    htmlUrl: 'https://github.com/RohannShetty/gitbook-downloader/releases/tag/v11.0.1',
    assets: [],
  },
  recentCommits: [
    {
      sha: 'abc1234',
      message: 'Fix something',
      date: '2026-08-30',
      author: 'Rohan Shetty',
      url: 'https://github.com/RohannShetty/gitbook-downloader/commit/abc1234',
    },
  ],
} as unknown as DocHarvestGithubData;

describe('focus-visible outline standardisation on interactive buttons', () => {
  it('AgentEcosystemShowcase — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<AgentEcosystemShowcase />);
    verifyFocusVisibleButtons(container, 'AgentEcosystemShowcase');
  });

  it('DocTypeSelector — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<DocTypeSelector />);
    verifyFocusVisibleButtons(container, 'DocTypeSelector');
  });

  it('ExportStudioPreview — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<ExportStudioPreview />);
    verifyFocusVisibleButtons(container, 'ExportStudioPreview');
  });

  it('FaqSection — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<FaqSection />);
    verifyFocusVisibleButtons(container, 'FaqSection');
  });

  it('Footer — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<Footer />);
    verifyFocusVisibleButtons(container, 'Footer');
  });

  it('GithubReleaseFeed — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<GithubReleaseFeed data={mockGithubData} />);
    verifyFocusVisibleButtons(container, 'GithubReleaseFeed');
  });

  it('Header — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(
      <ThemeProvider>
        <Header onOpenInstallModal={() => {}} />
      </ThemeProvider>,
    );
    verifyFocusVisibleButtons(container, 'Header');
  });

  it('Hero — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<Hero onOpenInstallModal={() => {}} />);
    verifyFocusVisibleButtons(container, 'Hero');
  });

  it('InstallModal — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<InstallModal isOpen={true} onClose={() => {}} />);
    verifyFocusVisibleButtons(container, 'InstallModal');
  });

  it('McpShowcase — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<McpShowcase />);
    verifyFocusVisibleButtons(container, 'McpShowcase');
  });

  it('OutputContract — buttons with cursor-pointer have focus-visible classes', () => {
    const { container } = render(<OutputContract />);
    verifyFocusVisibleButtons(container, 'OutputContract');
  });
});
