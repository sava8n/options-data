import { useMemo } from 'react';

import { FRONT_EXPIRY } from '../../config';
import { useGEXByStrike } from '../../hooks/useGEXByStrike';
import { useOIByStrike } from '../../hooks/useOIByStrike';
import { useProbCurves } from '../../hooks/useProbCurves';
import { useSpotHistory } from '../../hooks/useSpotHistory';
import { frontExpiry } from '../../utils/expiry';
import SpotHistoryPanel from './SpotHistoryPanel';
import { buildLevels, buildQuantileBand } from './levels';

export default function SpotHistorySection({ currency }: { currency: string }) {
  const { data, isLoading, isError, error } = useSpotHistory(currency);
  const candles = data?.candles ?? [];

  // options-derived levels
  const gex = useGEXByStrike(currency);
  const oiAll = useOIByStrike(currency);
  const front = oiAll.data ? frontExpiry(oiAll.data.expiries, FRONT_EXPIRY) : undefined;
  const oiFront = useOIByStrike(currency, front);
  const prob = useProbCurves(currency);
  const levels = useMemo(
    () => buildLevels(gex.data, oiAll.data, oiFront.data),
    [gex.data, oiAll.data, oiFront.data],
  );
  const band = useMemo(() => buildQuantileBand(prob.data, front), [prob.data, front]);

  return (
    <section className="panel panel--full">
      <div className="panel__title">
        <span className="panel__title-main">MARKET</span>
        <span className="panel__title-sub">{currency}_USDC · 1D</span>
      </div>
      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING MARKET…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && candles.length < 2 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {candles.length} PTS</div>
        )}
        {!isLoading && !isError && candles.length >= 2 && (
          <SpotHistoryPanel candles={candles} levels={levels} band={band} />
        )}
      </div>
    </section>
  );
}
