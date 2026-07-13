import { useState } from 'react';

import { FRONT_EXPIRY } from '../../config';
import { useOIByStrike } from '../../hooks/useOIByStrike';
import { frontExpiry } from '../../utils/expiry';
import { expiryLabel } from '../../utils/format';
import OIByStrikePanel from './OIByStrikePanel';
import OIStatTiles from './OIStatTiles';

export default function OIByStrikeSection({ currency }: { currency: string }) {
  const all = useOIByStrike(currency);
  const expiries = all.data?.expiries ?? [];
  const front = frontExpiry(expiries, FRONT_EXPIRY);

  // null = untouched, take the front expiry;
  // "" = user asked for all expirations
  const [picked, setPicked] = useState<string | null>(null);
  const kept = picked !== null && (picked === '' || expiries.includes(picked));
  const selected = kept ? (picked as string) : front ?? '';

  const { data, isLoading, isError, error } = useOIByStrike(currency, selected || null);

  const points = data?.points.length ?? 0;

  return (
    <section className="panel">
      <div className="panel__title">
        <span className="panel__title-main">OPEN INTEREST BY STRIKE</span>
        <span className="panel__title-sub">CONTRACTS · ITM/OTM × STRIKE</span>
        <label className="expiry">
          <span className="expiry__label">EXPIRY</span>
          <select
            className="expiry__select"
            value={selected}
            onChange={(e) => setPicked(e.target.value)}
          >
            <option value="">ALL EXPIRATIONS</option>
            {expiries.map((iso) => (
              <option key={iso} value={iso}>
                {expiryLabel(iso)}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING OPEN INTEREST…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && data && points < 1 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {points} PTS</div>
        )}
        {!isLoading && !isError && data && points >= 1 && <OIByStrikePanel data={data} />}
      </div>

      {!isLoading && !isError && data && points >= 1 && <OIStatTiles data={data} />}
    </section>
  );
}
