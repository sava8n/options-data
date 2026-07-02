import type { UseQueryResult } from '@tanstack/react-query';
import type { IVSurfaceResponse } from '../types';
import Header from './Header';
import StatusBar from './StatusBar';
import IVSurfacePanel from './IVSurfacePanel';

interface Props {
  currency: string;
  query: UseQueryResult<IVSurfaceResponse, Error>;
}

export default function Dashboard({ currency, query }: Props) {
  const { data, isLoading, isError, error, isFetching, dataUpdatedAt } = query;
  const points = data?.points.length ?? 0;

  return (
    <div className="dashboard">
      <Header currency={currency} data={data} isFetching={isFetching} isError={isError} />

      <main className="panel">
        <div className="panel__title">
          <span className="panel__title-main">IMPLIED VOLATILITY SURFACE</span>
          <span className="panel__title-sub">3D · DELTA × EXPIRY × IV · SOURCE DERIBIT</span>
        </div>
        <div className="panel__body">
          {isLoading && <div className="panel__msg">LOADING SURFACE…</div>}
          {isError && (
            <div className="panel__msg panel__msg--err">
              ERR · {error?.message ?? 'REQUEST FAILED'}
            </div>
          )}
          {!isLoading && !isError && data && points < 4 && (
            <div className="panel__msg panel__msg--warn">
              INSUFFICIENT DATA · {points} PTS
            </div>
          )}
          {!isLoading && !isError && data && points >= 4 && <IVSurfacePanel data={data} />}
        </div>
      </main>

      <StatusBar
        data={data}
        isFetching={isFetching}
        isError={isError}
        dataUpdatedAt={dataUpdatedAt}
      />
    </div>
  );
}
