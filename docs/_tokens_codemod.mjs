// One-off codemod: replace hardcoded Tailwind palette color classes
// (numeric shades) with semantic design tokens from app/globals.css.
// ONLY transforms palette class substrings; all other source text
// (version strings, aria attrs, focus-visible, imports, layout classes)
// is preserved verbatim. Safe to re-run.

import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join, relative } from 'path';
import { fileURLToPath } from 'url';

const ROOT = fileURLToPath(new URL('.', import.meta.url)); // docs root

const PALETTES = [
  'zinc', 'slate', 'gray', 'grey', 'indigo', 'amber', 'rose', 'cyan',
  'emerald', 'orange', 'red', 'green', 'blue', 'violet', 'fuchsia',
  'pink', 'yellow', 'lime', 'sky', 'teal', 'neutral', 'stone',
];
const P = PALETTES.join('|');
const PRE = '(text|bg|border|fill|stroke|ring)';

// Collapse `X dark:Y` pairs (same prefix+palette) -> semantic of the light
// variant, preserving the light opacity and dropping the redundant dark
// variant (semantic tokens already adapt to the color scheme).
const pairRe = new RegExp(
  `\\b${PRE}-(${P})-(\\d+)(?:\\/(\\d+))?\\s+dark:\\1-(${P})-(\\d+)(?:\\/(\\d+))?`,
  'g',
);

// Replace any remaining standalone palette shade classes -> semantic token.
// Optional leading `dark:` is dropped (semantic adapts).
const singleRe = new RegExp(
  `(?:dark:)?${PRE}-(${P})-(\\d+)(?:\\/(\\d+))?`,
  'g',
);

function semanticClass(prefix, palette, shade) {
  const n = Number(shade);
  const darkSurfaces = ['zinc', 'slate', 'gray', 'grey', 'neutral', 'stone'];
  const isDarkSurface = darkSurfaces.includes(palette);
  if (prefix === 'text') {
    if (isDarkSurface) return n <= 200 ? 'text-foreground' : 'text-muted-foreground';
    if (palette === 'cyan') return 'text-cyan';
    if (palette === 'emerald') return 'text-emerald';
    if (['indigo', 'blue', 'violet', 'fuchsia'].includes(palette)) return 'text-primary';
    if (['amber', 'yellow', 'orange'].includes(palette)) return 'text-accent';
    if (['rose', 'red', 'pink'].includes(palette)) return 'text-destructive';
    return 'text-foreground';
  }
  if (prefix === 'bg') {
    if (isDarkSurface) return n >= 950 ? 'bg-card' : 'bg-secondary';
    if (palette === 'cyan') return 'bg-cyan';
    if (palette === 'emerald') return 'bg-emerald';
    if (['indigo', 'blue', 'violet', 'fuchsia'].includes(palette)) return 'bg-primary';
    if (['amber', 'yellow', 'orange'].includes(palette)) return 'bg-accent';
    if (['rose', 'red', 'pink'].includes(palette)) return 'bg-destructive';
    return 'bg-secondary';
  }
  if (prefix === 'border') {
    if (isDarkSurface) return 'border-border';
    if (palette === 'cyan') return 'border-cyan';
    if (palette === 'emerald') return 'border-emerald';
    if (['indigo', 'blue', 'violet', 'fuchsia'].includes(palette)) return 'border-primary';
    if (['amber', 'yellow', 'orange'].includes(palette)) return 'border-accent';
    if (['rose', 'red', 'pink'].includes(palette)) return 'border-destructive';
    return 'border-border';
  }
  if (prefix === 'fill') {
    if (['rose', 'red', 'pink'].includes(palette)) return 'fill-destructive';
    if (palette === 'cyan') return 'fill-cyan';
    if (palette === 'emerald') return 'fill-emerald';
    if (['amber', 'yellow', 'orange'].includes(palette)) return 'fill-accent';
    if (['indigo', 'blue', 'violet', 'fuchsia'].includes(palette)) return 'fill-primary';
    return 'fill-foreground';
  }
  if (prefix === 'stroke') {
    if (['rose', 'red', 'pink'].includes(palette)) return 'stroke-destructive';
    if (palette === 'cyan') return 'stroke-cyan';
    if (palette === 'emerald') return 'stroke-emerald';
    if (['amber', 'yellow', 'orange'].includes(palette)) return 'stroke-accent';
    if (['indigo', 'blue', 'violet', 'fuchsia'].includes(palette)) return 'stroke-primary';
    return 'stroke-foreground';
  }
  if (prefix === 'ring') {
    if (isDarkSurface) return 'ring-border';
    if (palette === 'cyan') return 'ring-cyan';
    if (palette === 'emerald') return 'ring-emerald';
    if (['indigo', 'blue'].includes(palette)) return 'ring-primary';
    if (['amber', 'orange', 'yellow'].includes(palette)) return 'ring-accent';
    if (['rose', 'red', 'pink'].includes(palette)) return 'ring-destructive';
    return 'ring-border';
  }
  return prefix + '-' + palette;
}

function transform(src) {
  // 1. collapse dark: pairs
  src = src.replace(pairRe, (_m, prefix, palette, shade, op) => {
    return semanticClass(prefix, palette, shade) + (op ? '/' + op : '');
  });
  // 2. replace remaining standalone palette classes
  src = src.replace(singleRe, (_m, palette, shade, op) => {
    // prefix is captured implicitly via the match text before palette;
    // re-derive prefix from the full match tail.
    return '';
  });
  return src;
}

// ---- walk docs/components/**/*.tsx (excluding __tests__) ----
function walk(dir, acc) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith('__')) continue;
    const full = join(dir, e.name);
    if (e.isDirectory()) walk(full, acc);
    else if (e.name.endsWith('.tsx')) acc.push(full);
  }
}

const files = [];
walk(join(ROOT, 'components'), files);

let total = 0;
for (const f of files) {
  const before = readFileSync(f, 'utf8');
  let after = before;

  // step 1: pairs
  pairRe.lastIndex = 0;
  after = after.replace(pairRe, (m, prefix, palette, shade, op) => {
    return semanticClass(prefix, palette, shade) + (op ? '/' + op : '');
  });
  // step 2: standalone (with optional dark: prefix)
  singleRe.lastIndex = 0;
  after = after.replace(singleRe, (m, palette, shade, op) => {
    // extract prefix from the matched substring
    const prefix = m.replace(/(dark:)?(text|bg|border|fill|stroke|ring)-.*/, '$2');
    return semanticClass(prefix, palette, shade) + (op ? '/' + op : '');
  });

  if (after !== before) {
    writeFileSync(f, after, 'utf8');
    const rel = relative(ROOT, f);
    // count replacements for reporting
    const re = new RegExp(`\\b${PRE}-(${P})-\\d+(?:/\\d+)?`, 'g');
    const remain = (before.match(re) || []).length - (after.match(re) || []).length;
    const removed = before.length - after.length;
    total += remain;
    console.log(`${rel}: ~${remain} palette classes replaced (src len ${before.length} -> ${after.length})`);
  }
}
console.log(`\nTotal palette classes replaced across ${files.length} files: ${total}`);
console.log('Remaining palette shades in source:', (() => {
  let n = 0;
  for (const f of files) {
    const s = readFileSync(f, 'utf8');
    const re = new RegExp(`\\b${PRE}-(${P})-\\d+(?:/\\d+)?`, 'g');
    let m;
    while ((m = re.exec(s))) n++;
  }
  return n;
})());
