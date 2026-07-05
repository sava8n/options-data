import { useSpot } from '../hooks/useSpot';

function formatSpot(spot?: number): string {
  if (spot == null) return '—';
  return spot.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

function Field({ k, v, amber }: { k: string; v: string; amber?: boolean }) {
  return (
    <div className="field">
      <span className="field__k">{k}</span>
      <span className={`field__v${amber ? ' field__v--amber' : ''}`}>{v}</span>
    </div>
  );
}

export default function Header({ currency }: { currency: string }) {
  const { data } = useSpot(currency);

  return (
    <header className="header">
      <div className="header__brand">◆ OPTIONS&nbsp;DASHBOARD</div>
      <div className="header__fields">
        <Field k="SYM" v={`${currency}-USD`} />
        <Field k="SPOT" v={`$${formatSpot(data?.spot)}`} amber />
        <Field k="SRC" v="DERIBIT" />
      </div>
    </header>
  );
}
