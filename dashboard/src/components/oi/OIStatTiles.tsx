import { useMemo } from 'react';
import type { OIByStrikeResponse } from '../../types';
import { oiFull, usdFull } from '../../utils/format';

function Tile({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className={`oi-stat oi-stat--${accent}`}>
      <span className="oi-stat__label">{label}</span>
      <span className="oi-stat__value">{value}</span>
    </div>
  );
}

export default function OIStatTiles({ data }: { data: OIByStrikeResponse }) {
  const stats = useMemo(() => {
    let callOI = 0;
    let putOI = 0;
    for (const p of data.points) {
      callOI += p.itm_calls + p.otm_calls;
      putOI += p.itm_puts + p.otm_puts;
    }
    const totalOI = callOI + putOI;
    return {
      callOI,
      putOI,
      totalOI,
      pcRatio: callOI > 0 ? putOI / callOI : null,
      notional: totalOI * data.spot, // Deribit coin option = 1 coin/contract
      maxPain: data.max_pain,
    };
  }, [data]);

  return (
    <div className="oi-stats">
      <Tile label="CALL OPEN INTEREST" value={oiFull(stats.callOI)} accent="call" />
      <Tile label="PUT OPEN INTEREST" value={oiFull(stats.putOI)} accent="put" />
      <Tile label="TOTAL OPEN INTEREST" value={oiFull(stats.totalOI)} accent="total" />
      <Tile
        label="PUT/CALL RATIO"
        value={stats.pcRatio != null ? stats.pcRatio.toFixed(2) : '—'}
        accent="pcr"
      />
      <Tile label="NOTIONAL VALUE" value={usdFull(stats.notional)} accent="notional" />
      {stats.maxPain != null && (
        <Tile label="MAX PAIN PRICE" value={usdFull(stats.maxPain)} accent="maxpain" />
      )}
    </div>
  );
}
