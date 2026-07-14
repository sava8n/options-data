// Shared display formatters for chart axes and labels

// Deribit expiries are at 08:00 UTC; 
// Format like "04JUL26" (day + upper month + 2-digit year).
export function expiryLabel(iso: string): string {
  const d = new Date(iso);
  const day = String(d.getUTCDate()).padStart(2, '0');
  const mon = d
    .toLocaleString('en-US', { month: 'short', timeZone: 'UTC' })
    .toUpperCase();
  const yr = String(d.getUTCFullYear()).slice(-2);
  return `${day}${mon}${yr}`;
}

// strike axis: 62000 -> "62k"
export const strikeFmt = (v: number) => `${(v / 1000).toLocaleString('en-US')}k`;

// open interest (contracts), abbreviated: 62000 -> "62k"
export const oiFmt = (v: number) =>
  v >= 1000
    ? `${(v / 1000).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`
    : `${Math.round(v)}`;

// open interest (contracts), full: 1234567 -> "1,234,567"
export const oiFull = (v: number) =>
  v.toLocaleString('en-US', { maximumFractionDigits: 0 });

// USD, abbreviated: 12_500_000 -> "$12.5M"
export const usdShort = (v: number) => {
  if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toLocaleString('en-US', { maximumFractionDigits: 1 })}B`;
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toLocaleString('en-US', { maximumFractionDigits: 1 })}M`;
  if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`;
  return `$${Math.round(v)}`;
};

// USD, full: 61500 -> "$61,500.00"
export const usdFull = (v: number) =>
  `$${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

// price, whole units, unprefixed for price axes: 61500.4 -> "61,500"
export const priceWhole = (v: number) =>
  v.toLocaleString('en-US', { maximumFractionDigits: 0 });

// IV fraction: 0.42 -> "42%"
export const ivFmt = (v: number) => `${Math.round(v * 100)}%`;

// DVOL index level: 0.382 -> "38.2"
export const dvolFmt = (v: number) => (v * 100).toFixed(1);

// coin-equivalent contracts, abbreviated, sign-aware: -94384.5 -> "-94.4k"
export const coinEquiv = (v: number) => {
  const abs = Math.abs(v);
  const body =
    abs >= 1000
      ? `${(abs / 1000).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`
      : `${Math.round(abs)}`;
  return v < 0 ? `-${body}` : body;
};

// delta variant with explicit plus: 2470 -> "+2.5k"
export const coinEquivSigned = (v: number) => (v > 0 ? `+${coinEquiv(v)}` : coinEquiv(v));

// coin-equivalent contracts, full: 94384.5 -> "94,384.5"
export const coinFull = (v: number) =>
  v.toLocaleString('en-US', { maximumFractionDigits: 1 });

// signed percent: 12.34 -> "+12.3%"
export const signedPct = (v: number) =>
  `${v > 0 ? '+' : ''}${v.toLocaleString('en-US', { maximumFractionDigits: 1 })}%`;
