import type {
  GEXByStrikeResponse,
  OIByStrikePoint,
  OIByStrikeResponse,
  ProbCurvesResponse,
} from '../../types';
import { SPOT_CHART_LEVELS } from '../../config';
import { CALL, PUT } from '../../theme/charts';
import { expiryLabel, oiFmt, usdShort } from '../../utils/format';

export interface PriceLevel {
  price: number;
  title: string;
  color: string;
}

export interface QuantileBand {
  p16: number | null;
  p50: number | null;
  p84: number | null;
}

const FLIP = '#ff3b30';
const MAX_PAIN = '#b06cf0';
const TARGET_TTE = SPOT_CHART_LEVELS.bandDte / 365.25; // day-count

// Deribit monthlies settle on the last Friday of a month
function isMonthly(iso: string): boolean {
  const d = new Date(iso);
  if (d.getUTCDay() !== 5) return false;
  return new Date(d.getTime() + 7 * 86_400_000).getUTCMonth() !== d.getUTCMonth();
}

export function frontMonthlyExpiry(expiries: string[]): string | undefined {
  return expiries.find(isMonthly) ?? expiries[0];
}

// largest strike of one option side; undefined when the side has no OI
function wall(
  pts: OIByStrikePoint[],
  side: (p: OIByStrikePoint) => number,
): { strike: number; oi: number } | undefined {
  return pts
    .map((p) => ({ strike: p.strike, oi: side(p) }))
    .filter((w) => w.oi > 0)
    .reduce<{ strike: number; oi: number } | undefined>(
      (best, w) => (best && best.oi >= w.oi ? best : w),
      undefined,
    );
}

// Biggest strike by weight. Median of the run of comparably big neighbors
// (gap <= gexClusterMaxGap grid steps, weight >= gexClusterMinWeight of the max)
// when such a stack exists. Weight is summed over the cluster.
function clusterLevel(
  pts: { strike: number; weight: number }[],
): { price: number; weight: number } | undefined {
  const grid = pts.map((p) => p.strike).sort((a, b) => a - b);
  const steps = grid
    .slice(1)
    .map((s, i) => s - grid[i])
    .sort((a, b) => a - b);
  const maxGap = SPOT_CHART_LEVELS.gexClusterMaxGap * (steps[Math.floor(steps.length / 2)] ?? 0);

  const sorted = pts.filter((p) => p.weight > 0).sort((a, b) => a.strike - b.strike);
  if (sorted.length === 0) return undefined;

  let top = 0;
  for (let i = 1; i < sorted.length; i++) if (sorted[i].weight > sorted[top].weight) top = i;
  const minWeight = SPOT_CHART_LEVELS.gexClusterMinWeight * sorted[top].weight;

  let lo = top;
  while (lo > 0 && sorted[lo].strike - sorted[lo - 1].strike <= maxGap && sorted[lo - 1].weight >= minWeight) lo--;
  let hi = top;
  while (hi < sorted.length - 1 && sorted[hi + 1].strike - sorted[hi].strike <= maxGap && sorted[hi + 1].weight >= minWeight) hi++;

  const cluster = sorted.slice(lo, hi + 1);
  const mid = (cluster.length - 1) / 2;
  return {
    price: (cluster[Math.floor(mid)].strike + cluster[Math.ceil(mid)].strike) / 2,
    weight: cluster.reduce((sum, p) => sum + p.weight, 0),
  };
}

function deduplicate(levels: PriceLevel[]): PriceLevel[] {
  const kept: PriceLevel[] = [];
  for (const lvl of levels) {
    if (!kept.some((k) => Math.abs(lvl.price - k.price) <= SPOT_CHART_LEVELS.tolerance)) kept.push(lvl);
  }
  return kept;
}

// options-derived levels for the market strip:
// - GEX flip
// - front-month max pain
// - front-month call/put OI walls
// - clustered call-GEX resistance / put-GEX support
export function buildLevels(
  gex: GEXByStrikeResponse | undefined,
  oiAll: OIByStrikeResponse | undefined,
  oiFront: OIByStrikeResponse | undefined,
): PriceLevel[] {
  const spot = gex?.spot ?? oiAll?.spot;
  const inRange = (p: number) => spot != null && Math.abs(p / spot - 1) <= SPOT_CHART_LEVELS.range;

  const levels: PriceLevel[] = [];

  if (gex?.flip != null && inRange(gex.flip)) {
    levels.push({ price: gex.flip, title: 'GEX FLIP', color: FLIP });
  }

  if (oiFront?.max_pain != null && oiFront.expiry != null && inRange(oiFront.max_pain)) {
    levels.push({
      price: oiFront.max_pain,
      title: `MAX PAIN ${expiryLabel(oiFront.expiry)}`,
      color: MAX_PAIN,
    });
  }

  if (spot != null && oiFront) {
    const eligible = oiFront.points.filter((p) => inRange(p.strike));
    const callWall = wall(
      eligible.filter((p) => p.strike >= spot),
      (p) => p.itm_calls + p.otm_calls,
    );
    if (callWall) {
      levels.push({ price: callWall.strike, title: `CALL WALL ${oiFmt(callWall.oi)}`, color: CALL });
    }
    const putWall = wall(
      eligible.filter((p) => p.strike <= spot),
      (p) => p.itm_puts + p.otm_puts,
    );
    if (putWall) {
      levels.push({ price: putWall.strike, title: `PUT WALL ${oiFmt(putWall.oi)}`, color: PUT });
    }
  }

  if (spot != null && gex) {
    const eligible = gex.points.filter((p) => inRange(p.strike));
    const res = clusterLevel(
      eligible.filter((p) => p.strike >= spot).map((p) => ({ strike: p.strike, weight: p.call_gex })),
    );
    if (res) levels.push({ price: res.price, title: `GEX RES ${usdShort(res.weight)}`, color: CALL });
    // dealers are short put gamma, so put GEX is negative; magnitude is the weight
    const sup = clusterLevel(
      eligible.filter((p) => p.strike <= spot).map((p) => ({ strike: p.strike, weight: -p.put_gex })),
    );
    if (sup) levels.push({ price: sup.price, title: `GEX SUP ${usdShort(sup.weight)}`, color: PUT });
  }

  return deduplicate(levels);
}

// implied P16/P50/P84 at the expiry nearest the band horizon
export function buildQuantileBand(prob: ProbCurvesResponse | undefined): QuantileBand | undefined {
  if (!prob?.quantiles?.length) return undefined;
  const row = [...prob.quantiles].sort(
    (a, b) => Math.abs(a.tte_years - TARGET_TTE) - Math.abs(b.tte_years - TARGET_TTE),
  )[0];
  return { p16: row.p16, p50: row.p50, p84: row.p84 };
}
