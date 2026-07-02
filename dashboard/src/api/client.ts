import type { IVSurfaceResponse } from '../types';

export async function fetchIVSurface(currency = 'BTC'): Promise<IVSurfaceResponse> {
  const resp = await fetch(`/api/iv-surface?currency=${encodeURIComponent(currency)}`);
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail);
  }
  return (await resp.json()) as IVSurfaceResponse;
}
