# Design System — GitBook Downloader

## Overview
Modern, professional documentation interface for the GitBook Downloader tool. Built with Next.js 16.3.2 and TypeScript, featuring a glassmorphism design system, smooth interactions, and strong accessibility.

## Color Palette

| Variable | Hex | Usage |
|----------|-----|--------|
| `--background` | `#0A0A0C` | Base page background (dark mode) |
| `--foreground` | `#FAFAFA` | Primary text, light mode contrast |
| `--card` | `#121215` | Card backgrounds, panels |
| `--card-foreground` | `#FAFAFA` | Text inside cards |
| `--primary` | `#6366F1` | Accent, links, primary buttons |
| `--primary-foreground` | `#FFFFFF` | Text on primary colors |
| `--secondary` | `#1A1A22` | Secondary accents, borders |
| `--secondary-foreground` | `#FAFAFA` | Secondary text |
| `--muted` | `#16161A` | Muted text, subtitles |
| `--accent` | `#F59E0B` | Gradient accent (blue→amber) |
| `--cyan` | `#06B6D4` | Highlight, code blocks |
| `--emerald` | `#10B981` | Success states, badges |
| `--destructive` | `#EF4444` | Error states, destructive actions |
| `--border` | `#E4E4E7` | Border color |
| `--ring` | `#6366F1` | Focus rings, highlights |

## Typography

- **Font Family**: `ui-sans-serif` (Geist Sans), `ui-monospace` (Geist Mono)
- **Hierarchy**:
  - `h1`: 700 weight, letter-spacing -0.02em, line-height 1.15
  - `h2`: 600 weight, letter-spacing -0.02em, line-height 1.15
  - `h3`–`h6`: 600 weight, letter-spacing -0.02em, line-height 1.15
- **Scale**: `--radius` (0.5rem), `--radius-md` (calc(var(--radius)-2px)), `--radius-lg` (calc(var(--radius)+2px))

## Layout & Components

### Glassmorphism Cards

All content containers use a layered glass effect:

- **`.glass-1`** (light mode): `rgba(0,0,0,0.02)` background, `blur(12px) saturate(120%)` backdrop, `1px solid rgba(255,255,255,0.06)` border
- **`.glass-2`** (light mode): `rgba(0,0,0,0.03)` background, `blur(16px) saturate(130%)` backdrop, `1px solid rgba(255,255,255,0.08)` border
- **`.glass-3`** (light mode): `rgba(0,0,0,0.04)` background, `blur(20px) saturate(140%)` backdrop, `1px solid rgba(255,255,255,0.10)` border

Light mode variants override all background/foreground colors accordingly.

### Focus States

- `*:focus-visible` → `outline: 2px solid var(--ring)`
- `outline-offset: 2px`
- `border-radius: calc(var(--radius) - 2px)`

### Gradient Accents

- `.text-gradient-accent`: Linear gradient `#6366F1 0%, #F59E0B 100%` applied to text with `-webkit-background-clip: text` and `-webkit-text-fill-color: transparent`

### Interactions

- **Terminal-like elements** (Hero, DocTypeSelector): Use `framer-motion` animations for smooth transitions
- **Focus-visible rings** for keyboard navigation
- **Reduced motion** support: All animations disabled when `prefers-reduced-motion: reduce`

## Component Library

| Component | Purpose | Key Properties |
|-----------|---------|----------------|
| `Header` | Site header with logo, nav, install modal | Fixed top, sticky on scroll |
| `Hero` | Interactive intro with terminal simulation | Centered, animated background grid |
| `DocTypeSelector` | Choose doc types (AST, Vector, etc.) | Tab-based, active indicator |
| `OutputContract` | Shows downloaded output format | Code block with syntax highlighting |
| `ExportStudioPreview` | Preview export studio UI | Dark theme, file browser mock |
| `FeatureMatrix` | Comparison matrix of features | Table with icons, hover states |
| `McpShowcase` | MCP tool showcase | Cards with icon + description |
| `PersonaShowcase` | User persona scenarios | Cards with use case text |
| `GithubReleaseFeed` | Live release feed | Horizontal scroll, GitHub badge |
| `FaqSection` | FAQ accordion | Collapsible sections |
| `Footer` | Bottom bar with links | Dark, minimal |

## Motion & Animation

- **Hero section**: Subtle parallax background grid (CSS-only)
- **Button hover**: Scale 1.05 + subtle glow on primary color
- **Card hover**: Slight lift (`translateY(-2px)`) + border brighten
- **Focus transitions**: Smooth 150ms transition
- **Scroll reveals**: IntersectionObserver for fade-in on scroll

## Accessibility

- **Contrast**: Minimum 4.5:1 for text (checked against palette)
- **Keyboard navigation**: Full tab order, logical focus
- **ARIA**: Proper roles, labels, and states
- **Screen reader**: Semantic HTML, alt text for all images
- **Reduced motion**: Respect `prefers-reduced-motion`

## Responsive Behavior

- **Mobile** (< 640px): Stack components vertically, larger tap targets
- **Tablet** (640-1024px): Adjust grid columns, wider hero
- **Desktop** (≥ 1024px): Two-column layout for FeatureMatrix, expanded footers

## Design Tokens (CSS Variables)

All colors, radii, shadows, and spacing defined in `globals.css` as shown above. These should be consumed exclusively — no hardcoded hex values elsewhere.

## Implementation Notes

- **Dark mode** is the default; light mode is a toggle in the footer
- **Glass effects** are additive (blur + semi-transparent background) — never opaque overlays
- **Typography** uses Geist Sans for readability; mono for code
- **Icons** sourced from `lucide-react` (Terminal, Download, ArrowRight, Check, Copy, Sparkles, Layers, Cpu, FileText)
- **Icons** are imported from `@/components/Icons`

---
*Design System v1.0*
*Version: 20260428*
*Owner: GitBook Downloader Team*
