import { useMemo } from 'react';

import { useIVSurface } from '../../hooks/useIVSurface';
import { filterByDTE } from '../../utils/dte';
import DTEControl from '../shared/DTEControl';
import { useDteWindow } from '../shared/useDteWindow';
import IVSurfacePanel from './IVSurfacePanel';

export default function IVSurfaceSection({ currency }: { currency: string }) {
  const { data, isLoading, isError, error } = useIVSurface(currency);

  const [dte, setDte] = useDteWindow();
  const windowed = useMemo(
    () => (data ? { ...data, points: filterByDTE(data.points, dte.min, dte.max) } : undefined),
    [data, dte],
  );
  const points = windowed?.points.length ?? 0;

  return (
    <main className="panel">
      <div className="panel__title">
        <span className="panel__title-main">IMPLIED VOLATILITY SURFACE</span>
        <span className="panel__title-sub">3D · DELTA × EXPIRY × IV</span>
        <DTEControl min={dte.min} max={dte.max} onChange={(min, max) => setDte({ min, max })} />
      </div>
      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING SURFACE…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && windowed && points < 4 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {points} PTS</div>
        )}
        {!isLoading && !isError && windowed && points >= 4 && <IVSurfacePanel data={windowed} />}
      </div>
    </main>
  );
}
