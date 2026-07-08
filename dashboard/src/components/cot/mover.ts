import type { CotReportRow } from '../../types';

// the category with the largest absolute week-over-week net change
export function biggestMover(rows: CotReportRow[]): CotReportRow | null {
  return rows.reduce<CotReportRow | null>((best, row) => {
    if (row.delta_net_btc == null) return best;
    if (best?.delta_net_btc == null) return row;
    return Math.abs(row.delta_net_btc) > Math.abs(best.delta_net_btc) ? row : best;
  }, null);
}
