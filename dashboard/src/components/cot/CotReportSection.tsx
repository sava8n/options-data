import type { CotMethod, CotWindow } from '../../api/client';
import { useCotReport } from '../../hooks/useCotReport';
import CotChangesTable from './CotChangesTable';
import CotStatTiles from './CotStatTiles';

export default function CotReportSection({
  currency,
  window,
  method,
}: {
  currency: string;
  window: CotWindow;
  method: CotMethod;
}) {
  const { data, isLoading, isError, error } = useCotReport(currency, window, method);

  return (
    <section className="panel panel--auto">
      <div className="panel__title">
        <span className="panel__title-main">COT REPORT · CME {currency} FUTURES</span>
        <span className="panel__title-sub">
          TFF FUTURES-ONLY · {currency} + MICRO · {currency}-EQUIV
        </span>
      </div>

      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING COT REPORT…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && data && (
          <div>
            <CotStatTiles data={data} />
            <CotChangesTable data={data} />
          </div>
        )}
      </div>
    </section>
  );
}
