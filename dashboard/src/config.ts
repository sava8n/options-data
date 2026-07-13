import type { FrontExpiry } from './utils/expiry';

// currency book shown on load
export const DEFAULT_CURRENCY = 'BTC';

// default DTE window
// near-dated expiries out to the front month
export const DEFAULT_MIN_DTE = 0;
export const DEFAULT_MAX_DTE = 30;

// nearest weekly/monthly expiry 
export const FRONT_EXPIRY: FrontExpiry = 'monthly';

// spot chart
// initial visible window, days of daily candles
export const SPOT_CHART_LOOKBACK_DAYS = 180;
// chart levels
export const SPOT_CHART_LEVELS = {
  range: 0.3, // levels beyond ±this of spot are off-chart noise
  tolerance: 499, // coincident levels within this distance collapse, in units
  gexClusterMinWeight: 0.5, // a neighbor counts as stacked at >= this fraction of the max weight
  gexClusterMaxGap: 1.5, // max stacked-neighbor gap, in units of the median grid step
} as const;
