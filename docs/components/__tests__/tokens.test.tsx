import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync } from 'fs';
import { resolve } from 'path';

/**
 * Audit: no hardcoded Tailwind palette color classes (with numeric shades)
 * may remain in component source. Semantic design tokens from globals.css
 * (e.g. `text-cyan`, `bg-card`, `text-muted-foreground`, `border-border`,
 * `text-primary`, `text-accent`, `text-destructive`) carry no numeric shade
 * and are the intended replacement target — they auto-adapt to the active
 * color scheme via the `@theme inline` block in `app/globals.css`.
 *
 * A numeric-shade palette class is, by definition, a hardcoded palette color.
 */

// Resolves docs/components regardless of whether `import.meta.url` is a file
// URL (vitest may transform it). Vitest runs with cwd = docs/.
const COMPONENTS_DIR = resolve(process.cwd(), 'components');

const PALETTES = [
  'zinc', 'slate', 'gray', 'grey', 'indigo', 'amber', 'rose', 'cyan',
  'emerald', 'orange', 'red', 'green', 'blue', 'violet', 'fuchsia',
  'pink', 'yellow', 'lime', 'sky', 'teal', 'neutral', 'stone',
] as const;

// Matches a hardcoded palette shade class, including variant prefixes
// (`dark:`, `hover:`, `group-hover:`) and opacity modifiers (`/10`).
// Semantic tokens like `text-cyan`, `bg-card`, `border-border/60` have NO
// numeric shade and are therefore NOT matched.
const PALETTE_SHADE_RE = new RegExp(
  `[a-zA-Z:]+-(?:${PALETTES.join('|')})-\\d+(?:/\\d+)?`,
  'g',
);

function findComponentFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('__')) continue; // exclude __tests__
    const full = resolve(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...findComponentFiles(full));
    } else if (entry.name.endsWith('.tsx')) {
      out.push(full);
    }
  }
  return out;
}

interface Violation {
  file: string;
  line: number;
  match: string;
}

function scanFile(file: string): Violation[] {
  const src = readFileSync(file, 'utf8');
  const violations: Violation[] = [];
  const rel = file.replace(/\\/g, '/').replace(/^.*docs\/components\//, '');
  let m: RegExpExecArray | null;
  PALETTE_SHADE_RE.lastIndex = 0;
  while ((m = PALETTE_SHADE_RE.exec(src)) !== null) {
    const start = m.index;
    const line = src.slice(0, start).split('\n').length;
    violations.push({ file: rel, line, match: m[0] });
  }
  return violations;
}

describe('design-tokens: no hardcoded palette color classes', () => {
  it('all component sources use semantic tokens only', () => {
    const files = findComponentFiles(COMPONENTS_DIR);
    expect(files.length).toBeGreaterThan(0);
    const violations = files.flatMap(scanFile);
    const report = violations
      .map((v) => `${v.file}:${v.line} → ${v.match}`)
      .join('\n');
    expect(violations, `\n${report || '(none)'}\n`).toHaveLength(0);
  });
});
