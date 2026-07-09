import { useCotHistory } from '../../hooks/useCotHistory';
import CotFlowPanel from './CotFlowPanel';

export default function CotFlowSection({
  currency,
  weeks,
}: {
  currency: string;
  weeks: number;
}) {
  const { data, isLoading, isError, error } = useCotHistory(currency);
  const points = data?.points.length ?? 0;

  return (
    <section className="panel">
      <div className="panel__title">
        <span className="panel__title-main">WOW NET FLOW</span>
        <span className="panel__title-sub">
          ΔNET {currency}-EQUIV × CATEGORY · LAST {weeks} REPORTS
        </span>
      </div>

      <div className="panel__body">
        {isLoading && <div className="panel__msg">LOADING COT HISTORY…</div>}
        {isError && (
          <div className="panel__msg panel__msg--err">
            ERR · {error?.message ?? 'REQUEST FAILED'}
          </div>
        )}
        {!isLoading && !isError && data && points < 2 && (
          <div className="panel__msg panel__msg--warn">INSUFFICIENT DATA · {points} PTS</div>
        )}
        {!isLoading && !isError && data && points >= 2 && (
          <CotFlowPanel data={data} weeks={weeks} />
        )}
      </div>
    </section>
  );
}
