import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { FaqSection } from '../FaqSection';
import { DocTypeSelector } from '../DocTypeSelector';
import { OutputContract } from '../OutputContract';
import { Hero } from '../Hero';
import { ExportStudioPreview } from '../ExportStudioPreview';
import { FAQ_ITEMS } from '../../data/showcaseData';

afterEach(() => {
  cleanup();
});

const noop = () => {};

// ─── FaqSection: accordion buttons with aria-expanded + aria-controls ─────────

describe('FaqSection ARIA patterns', () => {
  it('renders all FAQ accordion buttons', () => {
    render(<FaqSection />);
    expect(screen.getAllByRole('button')).toHaveLength(FAQ_ITEMS.length);
  });

  it('accordion buttons have aria-expanded reflecting open/closed state', () => {
    render(<FaqSection />);
    const buttons = screen.getAllByRole('button');
    // First FAQ starts open (openIndex = 0)
    expect(buttons[0]).toHaveAttribute('aria-expanded', 'true');
    // Others start closed
    expect(buttons[1]).toHaveAttribute('aria-expanded', 'false');
    expect(buttons[2]).toHaveAttribute('aria-expanded', 'false');
  });

  it('each accordion button has aria-controls with a non-empty value', () => {
    render(<FaqSection />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach((button) => {
      expect(button).toHaveAttribute('aria-controls');
      const targetId = button.getAttribute('aria-controls');
      expect(targetId).toBeTruthy();
      expect(targetId!.length).toBeGreaterThan(0);
    });
  });

  it('aria-controls on the open accordion references an existing content element', () => {
    render(<FaqSection />);
    const openButton = screen.getAllByRole('button')[0];
    const targetId = openButton.getAttribute('aria-controls');
    expect(targetId).toBeTruthy();
    expect(document.getElementById(targetId!)).toBeInTheDocument();
  });

  it('clicking a closed accordion button sets aria-expanded="true"', async () => {
    const user = userEvent.setup();
    render(<FaqSection />);
    const buttons = screen.getAllByRole('button');
    const secondButton = buttons[1];
    expect(secondButton).toHaveAttribute('aria-expanded', 'false');
    await user.click(secondButton);
    expect(secondButton).toHaveAttribute('aria-expanded', 'true');
  });

  it('clicking the open accordion button sets aria-expanded="false"', async () => {
    const user = userEvent.setup();
    render(<FaqSection />);
    const buttons = screen.getAllByRole('button');
    const firstButton = buttons[0];
    expect(firstButton).toHaveAttribute('aria-expanded', 'true');
    await user.click(firstButton);
    expect(firstButton).toHaveAttribute('aria-expanded', 'false');
  });
});

// ─── DocTypeSelector: toggle pills with aria-pressed ─────────────────────────

describe('DocTypeSelector ARIA patterns', () => {
  it('first framework pill has aria-pressed="true", others "false"', () => {
    render(<DocTypeSelector />);
    const pills = screen.getAllByRole('button');
    expect(pills[0]).toHaveAttribute('aria-pressed', 'true');
    expect(pills[1]).toHaveAttribute('aria-pressed', 'false');
    expect(pills[2]).toHaveAttribute('aria-pressed', 'false');
  });

  it('clicking a different pill updates aria-pressed', async () => {
    const user = userEvent.setup();
    render(<DocTypeSelector />);
    const pills = screen.getAllByRole('button');
    const thirdPill = pills[2];
    expect(thirdPill).toHaveAttribute('aria-pressed', 'false');
    await user.click(thirdPill);
    expect(thirdPill).toHaveAttribute('aria-pressed', 'true');
    expect(pills[0]).toHaveAttribute('aria-pressed', 'false');
  });
});

// ─── OutputContract: toggle cards with aria-pressed ──────────────────────────

describe('OutputContract ARIA patterns', () => {
  it('first format card has aria-pressed="true", others "false"', () => {
    render(<OutputContract />);
    const cards = screen.getAllByRole('button');
    expect(cards[0]).toHaveAttribute('aria-pressed', 'true');
    expect(cards[1]).toHaveAttribute('aria-pressed', 'false');
    expect(cards[2]).toHaveAttribute('aria-pressed', 'false');
    expect(cards[3]).toHaveAttribute('aria-pressed', 'false');
  });

  it('clicking a different card updates aria-pressed', async () => {
    const user = userEvent.setup();
    render(<OutputContract />);
    const cards = screen.getAllByRole('button');
    const thirdCard = cards[2];
    expect(thirdCard).toHaveAttribute('aria-pressed', 'false');
    await user.click(thirdCard);
    expect(thirdCard).toHaveAttribute('aria-pressed', 'true');
    expect(cards[0]).toHaveAttribute('aria-pressed', 'false');
  });
});

// ─── Hero: agent pills (aria-pressed) + terminal tabs (role=tab, aria-selected) ─

describe('Hero ARIA patterns', () => {
  describe('agent selector pills', () => {
    it('selected agent pill has aria-pressed="true"', () => {
      render(<Hero onOpenInstallModal={noop} />);
      const cursorPill = screen.getByRole('button', { name: 'Cursor' });
      expect(cursorPill).toHaveAttribute('aria-pressed', 'true');
    });

    it('non-selected agent pills have aria-pressed="false"', () => {
      render(<Hero onOpenInstallModal={noop} />);
      const codexPill = screen.getByRole('button', { name: 'Codex CLI' });
      expect(codexPill).toHaveAttribute('aria-pressed', 'false');
    });

    it('clicking a different agent updates aria-pressed', async () => {
      const user = userEvent.setup();
      render(<Hero onOpenInstallModal={noop} />);
      const codexPill = screen.getByRole('button', { name: 'Codex CLI' });
      expect(codexPill).toHaveAttribute('aria-pressed', 'false');
      await user.click(codexPill);
      expect(codexPill).toHaveAttribute('aria-pressed', 'true');
    });
  });

  describe('terminal tabs', () => {
    it('all tab buttons have role="tab"', () => {
      render(<Hero onOpenInstallModal={noop} />);
      expect(screen.getAllByRole('tab')).toHaveLength(4);
    });

    it('active tab has aria-selected="true"', () => {
      render(<Hero onOpenInstallModal={noop} />);
      const activeTab = screen.getByRole('tab', { name: /Crawl Logs/i });
      expect(activeTab).toHaveAttribute('aria-selected', 'true');
    });

    it('inactive tabs have aria-selected="false"', () => {
      render(<Hero onOpenInstallModal={noop} />);
      const astTab = screen.getByRole('tab', { name: /AST Filter/i });
      expect(astTab).toHaveAttribute('aria-selected', 'false');
    });

    it('clicking a different tab updates aria-selected', async () => {
      const user = userEvent.setup();
      render(<Hero onOpenInstallModal={noop} />);
      const astTab = screen.getByRole('tab', { name: /AST Filter/i });
      await user.click(astTab);
      expect(astTab).toHaveAttribute('aria-selected', 'true');
      const terminalTab = screen.getByRole('tab', { name: /Crawl Logs/i });
      expect(terminalTab).toHaveAttribute('aria-selected', 'false');
    });
  });
});

// ─── ExportStudioPreview: tabs with role="tab" and aria-selected ──────────────

describe('ExportStudioPreview ARIA patterns', () => {
  it('all four tab buttons have role="tab"', () => {
    render(<ExportStudioPreview />);
    expect(screen.getAllByRole('tab')).toHaveLength(4);
  });

  it('active tab has aria-selected="true"', () => {
    render(<ExportStudioPreview />);
    const markdownTab = screen.getByRole('tab', { name: /book\.md/i });
    expect(markdownTab).toHaveAttribute('aria-selected', 'true');
  });

  it('inactive tabs have aria-selected="false"', () => {
    render(<ExportStudioPreview />);
    const ragTab = screen.getByRole('tab', { name: /dataset\.jsonl/i });
    expect(ragTab).toHaveAttribute('aria-selected', 'false');
  });

  it('clicking a different tab updates aria-selected', async () => {
    const user = userEvent.setup();
    render(<ExportStudioPreview />);
    const ragTab = screen.getByRole('tab', { name: /dataset\.jsonl/i });
    await user.click(ragTab);
    expect(ragTab).toHaveAttribute('aria-selected', 'true');
    const markdownTab = screen.getByRole('tab', { name: /book\.md/i });
    expect(markdownTab).toHaveAttribute('aria-selected', 'false');
  });
});
