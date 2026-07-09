import { useIsFetching, useQueryClient } from '@tanstack/react-query';

import { useStats } from '../hooks/useStats';
import { ivFmt } from '../utils/format';

function formatSpot(spot?: number): string {
  if (spot == null) return '—';
  return spot.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

// DVOL index level: 0.382 -> "38.2"
const dvolFmt = (v: number) => (v * 100).toFixed(1);

function Field({ k, v, amber }: { k: string; v: string; amber?: boolean }) {
  return (
    <div className="field">
      <span className="field__k">{k}</span>
      <span className={`field__v${amber ? ' field__v--amber' : ''}`}>{v}</span>
    </div>
  );
}

export default function Header({ currency }: { currency: string }) {
  const { data } = useStats(currency);
  const queryClient = useQueryClient();
  const busy = useIsFetching() > 0;

  // invalidate rather than refetch: 
  // mounted queries refetch now, the rest when their tab is next opened
  const refresh = () => queryClient.invalidateQueries();

  return (
    <header className="header">
      <div className="header__brand">◆ DATADESK</div>
      <div className="header__fields">
        <Field k="SYM" v={`${currency}-USD`} />
        <Field k="SPOT" v={`$${formatSpot(data?.spot)}`} amber />
        <Field k="DVOL" v={data?.dvol != null ? dvolFmt(data.dvol) : '—'} />
        <Field k="IV RANK" v={data?.dvol_rank != null ? ivFmt(data.dvol_rank) : '—'} />
        <Field
          k="IV30/RV30"
          v={
            data?.iv30 != null && data?.rv30 != null
              ? `${ivFmt(data.iv30)}/${ivFmt(data.rv30)}`
              : '—'
          }
        />
        <Field k="SRC" v="DERIBIT" />
      </div>
      <button className="refresh" onClick={refresh} disabled={busy}>
        {busy ? '⟳ SYNCING' : '⟳ REFRESH'}
      </button>
    </header>
  );
}
