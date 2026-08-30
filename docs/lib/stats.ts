// Centralized marketing stats for DocHarvest.
// Single source of truth — components import STATS from here instead of hardcoding.
// Bump values here; consumers update automatically.

export const STATS = {
  agentsShipped: 12,        // harnesses supported by FastMCP integration
  harnesses: 15,            // total harnesses with shim/install path
  pagesCaptured: 364,       // pages in the canonical OpenAlgo reference capture
  reductionPct: 89,         // average token reduction vs raw HTML
  speedPagesPerSec: 20.0,   // sustained throughput on a 4-core worker pool
  captureTimeSec: 18.2,     // wall-clock seconds for the reference capture
} as const;

export type DocHarvestStats = typeof STATS;