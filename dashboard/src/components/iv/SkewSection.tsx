import { useMemo } from 'react';

import { useSkew } from '../../hooks/useSkew';
import { filterByDTE } from '../../utils/dte';
import DTEControl from '../shared/DTEControl';
import { useDteWindow } from '../shared/useDteWindow';
import SkewPanel from './SkewPanel';

export default function SkewSection({ currency }: { currency: string }) {
  const { data, isLoading, isError, error } = useSkew(currency);

  const [dte, setDte] = useDteWindow();
  const windowed = useMemo(
    () => (data ? { ...data, points: filterByDTE(data.points, dte.min, dte.max) } : undefined),
    [data, dte],
  );
  const points = windowed?.points.length ?? 0;

  return (
    <section className="panel">
      <div className="panel__title">
        <span className="panel__title-main">25Δ SKEW</span>
        <span className="panel__title-sub">2D · RR / BF × EXPIRY</span>
        <DTEControl min={dte.min} max={dte.max} onChange={(min, max) => setDte({ min, max })} />
      </div>
      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING 25Δ SKEW…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && windowed && points < 3 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {points} PTS</div>
        )}
        {!isLoading && !isError && windowed && points >= 3 && <SkewPanel data={windowed} />}
      </div>
    </section>
  );
}
