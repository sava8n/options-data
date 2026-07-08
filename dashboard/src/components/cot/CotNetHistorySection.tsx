import { useCotHistory } from '../../hooks/useCotHistory';
import { expiryLabel } from '../../utils/format';
import CotNetHistoryPanel from './CotNetHistoryPanel';

export default function CotNetHistorySection() {
  const { data, isLoading, isError, error } = useCotHistory();
  const points = data?.points.length ?? 0;

  return (
    <section className="panel panel--full">
      <div className="panel__title">
        <span className="panel__title-main">NET POSITIONING HISTORY</span>
        <span className="panel__title-sub">
          NET BTC-EQUIV × CATEGORY · WEEKLY · BTC PRICE STRIP
          {data?.micro_included_from
            ? ` · MICRO FROM ${expiryLabel(data.micro_included_from)}`
            : ''}
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
          <CotNetHistoryPanel data={data} />
        )}
      </div>
    </section>
  );
}
