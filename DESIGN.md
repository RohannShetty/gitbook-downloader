---
name: DocHarvest Design System
description: Modern, professional developer and documentation interface for DocHarvest (gitbook-downloader)
colors:
  primary: "#6366F1"
  primary-foreground: "#FFFFFF"
  background: "#0A0A0C"
  foreground: "#FAFAFA"
  card: "#121215"
  card-foreground: "#FAFAFA"
  secondary: "#1A1A22"
  secondary-foreground: "#FAFAFA"
  muted: "#16161A"
  muted-foreground: "#A1A1AA"
  accent: "#F59E0B"
  accent-foreground: "#0A0A0C"
  cyan: "#06B6D4"
  emerald: "#10B981"
  destructive: "#EF4444"
  border: "#1C1C22"
  ring: "#6366F1"
typography:
  display:
    fontFamily: "Geist Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 4rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Geist Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 3.5vw, 2.5rem)"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Geist Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Geist Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, monospace"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.05em"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  xl: "12px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.secondary-foreground}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.card-foreground}"
    rounded: "{rounded.lg}"
    padding: "24px"
  badge:
    backgroundColor: "{colors.muted}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.sm}"
    padding: "4px 10px"
---

# Design System: DocHarvest

## Overview

**Creative North Star: "The High-Throughput Research Lab"**

DocHarvest provides a high-density, precise engineering atmosphere designed for developers, AI engineers, and archival specialists. The visual language blends deep slate and obsidian surfaces with warm amber and indigo accents, laser-sharp typography, layered glass depth, and tactile interactive surfaces.

**Key Characteristics:**
- **Obsidian & Deep Slate Foundation**: High contrast dark-mode base with warm tinted layers avoiding pure harsh blacks.
- **Glassmorphism Depth Architecture**: Tiered backdrop blurs (`.glass-1`, `.glass-2`, `.glass-3`) providing structured elevation without arbitrary card nesting.
- **Precision Typography**: Clean sans-serif headings with tabular monospace accents for code, terminal metrics, and cryptographic hashes.
- **Restrained Vibrant Accents**: Deliberate focal points using indigo accents and amber highlights, avoiding generic purple SaaS templates.

## Colors

The palette balances technical precision with warmth, using dark obsidian tones and high-contrast accents.

### Primary
- **Indigo Accent** (`#6366F1`): Primary actions, links, active tab indicators, and interactive highlights.

### Secondary
- **Warm Amber** (`#F59E0B`): Feature badges, special highlights, and warning/attention callouts.

### Tertiary
- **Cyan & Emerald Telemetry** (`#06B6D4`, `#10B981`): Code block highlights, passing test indicators, and live release badges.

### Neutral
- **Obsidian Dark Background** (`#0A0A0C`): Base canvas background for dark mode.
- **Surface Dark Card** (`#121215`): Card surfaces, panel containers, and terminal backgrounds.
- **Secondary Slate Surface** (`#1A1A22`): Secondary containers, subtle badges, and sub-panels.
- **Muted Charcoal** (`#16161A`): Inactive states, subtle dividers, and inner code blocks.
- **Subtle Dark Border** (`#1C1C22`): Container borders and structural dividers.
- **Pure Crisp Text** (`#FAFAFA`): Primary headlines, body text, and contrast foreground.
- **Muted Steel Text** (`#A1A1AA`): Secondary subtitles, metadata, and labels.

### Named Rules
- **The Signal-First Rule**: Color is used strictly to communicate status, interaction, or hierarchy. Maximum 10% accent coverage on any screen.
- **The Tinted Surface Rule**: Surfaces are never neutral gray; dark backgrounds carry deep blue/charcoal undertones.

## Typography

**Display Font:** Geist Sans (with `ui-sans-serif, system-ui, sans-serif` fallback)  
**Body Font:** Geist Sans (with `ui-sans-serif, system-ui, sans-serif` fallback)  
**Label/Mono Font:** Geist Mono (with `ui-monospace, SFMono-Regular, monospace` fallback)

**Character:** Technical, crisp, high-legibility typographic pairing engineered for dense documentation, command-line snippets, and structural TOCs.

### Hierarchy
- **Display** (700 weight, `clamp(2.5rem, 5vw, 4rem)`, line-height 1.15, letter-spacing -0.02em): Hero titles and major landmark sections.
- **Headline** (600 weight, `clamp(1.75rem, 3.5vw, 2.5rem)`, line-height 1.2, letter-spacing -0.02em): Feature headings and category headers.
- **Title** (600 weight, `1.25rem`, line-height 1.3, letter-spacing -0.01em): Card titles, modal headers, and table headers.
- **Body** (400 weight, `1rem`, line-height 1.6, max line length 70ch): Descriptive copy, documentation text, and walkthroughs.
- **Label** (500 weight, `0.875rem`, letter-spacing 0.05em): Terminal prompts, metadata tags, badges, and table column titles.

### Named Rules
- **The Exact Ratio Rule**: Typographic hierarchy maintains at least a 1.25x scaling ratio between sequential heading tiers.
- **The Monospace Distinction Rule**: All commands, hashes, JSON snippets, and file paths are rendered strictly in monospace.

## Layout

- **Max Content Width**: 1280px (`max-w-7xl`) centered with responsive padding (`px-4 sm:px-6 lg:px-8`).
- **Vertical Spacing Scale**: 8px baseline (`gap-2`, `gap-4`, `gap-6`, `gap-8`, `gap-12`).
- **Responsive Breakpoints**:
  - Mobile (< 640px): Single-column stack, compact cards, enlarged touch targets (minimum 44px).
  - Tablet (640px - 1024px): 2-column feature grids, balanced sidebars.
  - Desktop (≥ 1024px): Multi-column layouts, expanded comparison matrices, and side-by-side terminal previews.

## Elevation & Depth

DocHarvest utilizes a tonal glassmorphism depth model instead of heavy drop shadows:

- **`.glass-1`**: `background: rgba(255,255,255,0.03)`, `backdrop-filter: blur(12px) saturate(120%)`, border `1px solid rgba(255,255,255,0.06)`. Used for base cards and subtle panels.
- **`.glass-2`**: `background: rgba(255,255,255,0.05)`, `backdrop-filter: blur(16px) saturate(130%)`, border `1px solid rgba(255,255,255,0.08)`. Used for interactive cards and floating headers.
- **`.glass-3`**: `background: rgba(255,255,255,0.07)`, `backdrop-filter: blur(20px) saturate(140%)`, border `1px solid rgba(255,255,255,0.10)`. Used for modals, dropdowns, and active focus surfaces.

### Named Rules
- **The Flat-By-Default Rule**: Containers rest on subtle border separation and tonal shifts; glow and elevation appear strictly on interactive hover or active state.

## Shapes

- **Corner Radii**: 4px (`rounded-sm` for badges), 6px (`rounded-md` for buttons/inputs), 8px (`rounded-lg` for standard cards), 12px (`rounded-xl` for hero preview containers and modals).
- **Borders**: 1px crisp borders (`border-border` / `#1C1C22`).

## Components

### Buttons
- **Shape**: Rounded corners (6px / `rounded-md`).
- **Primary**: Background `#6366F1`, text `#FFFFFF`, padding `10px 20px`, font weight 600. Hover: slight scale (1.02) and subtle indigo glow.
- **Secondary / Ghost**: Background `#1A1A22` (or transparent), border `1px solid #1C1C22`, text `#FAFAFA`, padding `10px 20px`.
- **Focus**: `outline: 2px solid var(--ring)`, `outline-offset: 2px`.

### Cards & Containers
- **Corner Style**: 8px or 12px radius.
- **Background**: `#121215` with `.glass-1` or `.glass-2` backdrop blur.
- **Internal Padding**: 24px (`p-6`).
- **Hover**: Subtle border brighten and lift (`translateY(-2px)`).

### Chips & Badges
- **Style**: Background `#16161A`, border `1px solid #1C1C22`, text `#A1A1AA`, padding `4px 10px`, font size `0.75rem` uppercase/monospace.

### Inputs & Terminal Displays
- **Terminal Glass**: `background: rgba(14, 14, 18, 0.85)`, backdrop blur 16px, border `1px solid #1C1C22`.
- **Code Highlighting**: Syntax tokens in amber, cyan, and emerald against dark canvas.

## Do's and Don'ts

### Do:
- **Do** maintain a minimum contrast ratio of 4.5:1 for all text against backgrounds.
- **Do** use solid, readable text colors rather than distracting multi-color gradient text.
- **Do** respect `prefers-reduced-motion: reduce` by disabling heavy motion transitions.
- **Do** provide full keyboard navigation with visible `:focus-visible` ring outlines.
- **Do** use distinct monospace styling for CLI commands, paths, and technical parameters.

### Don't:
- **Don't** nest cards inside cards; separate sections using spacing, hierarchy, and dividers.
- **Don't** use generic purple-to-violet SaaS gradients or unstyled default layouts.
- **Don't** use low-contrast gray text on colored badge backgrounds.
- **Don't** use decorative pulsing status animations on non-live static elements.
