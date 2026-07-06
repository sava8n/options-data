import { useSpotHistory } from '../../hooks/useSpotHistory';
import SpotHistoryPanel from './SpotHistoryPanel';

export default function SpotHistorySection({ currency }: { currency: string }) {
  const { data, isLoading, isError, error } = useSpotHistory(currency);
  const candles = data?.candles ?? [];

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
        {!isLoading && !isError && candles.length >= 2 && <SpotHistoryPanel candles={candles} />}
      </div>
    </section>
  );
}
