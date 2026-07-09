import type { ReactNode } from 'react';

import { COT_CATEGORIES } from '../../theme/charts';
import type { CotReportResponse } from '../../types';
import { coinEquivSigned, coinFull, expiryLabel, signedPct, usdShort } from '../../utils/format';
import { biggestMover } from './mover';

function Tile({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  accent?: string;
}) {
  return (
    <div className="cot-stat">
      <span
        className="cot-stat__label"
        style={accent ? { borderBottomColor: accent } : undefined}
      >
        {label}
      </span>
      <span className="cot-stat__value">{value}</span>
      {sub != null && <span className="cot-stat__sub">{sub}</span>}
    </div>
  );
}

export default function CotStatTiles({ data }: { data: CotReportResponse }) {
  const mover = biggestMover(data.rows);
  const moverColor = COT_CATEGORIES.find((c) => c.key === mover?.category)?.color;

  const deltaOI = data.delta_oi;
  const prevOI = deltaOI != null ? data.oi - deltaOI : null;
  const deltaOIPct = deltaOI != null && prevOI ? (deltaOI / Math.abs(prevOI)) * 100 : null;

  return (
    <div className="cot-stats">
      <Tile
        label="REPORT DATE (TUE)"
        value={
          <>
            {expiryLabel(data.report_date)}
            {data.is_new && <span className="cot-pill cot-pill--new">NEW</span>}
            {data.is_stale && <span className="cot-pill cot-pill--stale">STALE</span>}
          </>
        }
        sub={
          data.prev_report_date ? `PREV ${expiryLabel(data.prev_report_date)}` : undefined
        }
      />
      <Tile label="PUBLISHED (FRI)" value={expiryLabel(data.publication_date)} />
      <Tile
        label={`TOTAL OI · ${data.currency}-EQUIV`}
        value={coinFull(data.oi)}
        sub={
          deltaOI != null ? (
            <span className={deltaOI >= 0 ? 'cot-up' : 'cot-down'}>
              {coinEquivSigned(deltaOI)}
              {deltaOIPct != null ? ` (${signedPct(deltaOIPct)})` : ''} WOW
            </span>
          ) : undefined
        }
      />
      <Tile
        label="OI NOTIONAL"
        value={data.oi_usd != null ? usdShort(data.oi_usd) : '—'}
        sub={data.price != null ? `${data.currency} ${usdShort(data.price)}` : undefined}
      />
      <Tile
        label="BIGGEST WOW MOVER"
        value={mover ? <span style={{ color: moverColor }}>{mover.label}</span> : '—'}
        accent={moverColor}
        sub={
          mover?.delta_net != null ? (
            <span className={mover.delta_net >= 0 ? 'cot-up' : 'cot-down'}>
              {coinEquivSigned(mover.delta_net)} NET
            </span>
          ) : undefined
        }
      />
    </div>
  );
}
