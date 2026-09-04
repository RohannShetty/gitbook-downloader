// Centralized marketing stats for DocHarvest.
// Single source of truth — components import STATS from here instead of hardcoding.
// Bump values here; consumers update automatically.

export const STATS = {
  agentsShipped: 12,        // harness cards rendered in the showcase
  harnesses: 14,            // documented client configs in the README matrix
  pagesCaptured: 673,       // pages in the canonical full-suite OpenAlgo capture
  reductionPct: 83,         // measured token reduction vs raw HTML (82.8%)
  speedPagesPerSec: 37.0,   // 673 pages / 18.2 s on the canonical capture
  captureTimeSec: 18.2,     // wall-clock seconds for the reference capture
} as const;

export type DocHarvestStats = typeof STATS;