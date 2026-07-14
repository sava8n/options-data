import { useMemo } from 'react';

import { useTermStructure } from '../../hooks/useTermStructure';
import { filterByDTE } from '../../utils/dte';
import DTEControl from '../shared/DTEControl';
import { useDteWindow } from '../shared/useDteWindow';
import TermStructurePanel from './TermStructurePanel';

export default function TermStructureSection({ currency }: { currency: string }) {
  const { data, isLoading, isError, error } = useTermStructure(currency);

  const [dte, setDte] = useDteWindow();
  const windowed = useMemo(
    () => (data ? { ...data, points: filterByDTE(data.points, dte.min, dte.max) } : undefined),
    [data, dte],
  );
  const points = windowed?.points.length ?? 0;

  return (
    <section className="panel">
      <div className="panel__title">
        <span className="panel__title-main">TERM STRUCTURE</span>
        <span className="panel__title-sub">2D · ATM IV × EXPIRY</span>
        <DTEControl min={dte.min} max={dte.max} onChange={(min, max) => setDte({ min, max })} />
      </div>
      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING TERM STRUCTURE…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && windowed && points < 3 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {points} PTS</div>
        )}
        {!isLoading && !isError && windowed && points >= 3 && (
          <TermStructurePanel data={windowed} />
        )}
      </div>
    </section>
  );
}
