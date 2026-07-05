import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { fetchOIByStrike } from '../api/client';

export function useOIByStrike(currency = 'BTC', expiry?: string | null) {
  return useQuery({
    queryKey: ['oi-strike', currency, expiry ?? 'all'],
    queryFn: () => fetchOIByStrike(currency, expiry ?? undefined),
    // keep the dropdown + chart populated while switching expiry.
    placeholderData: keepPreviousData,
  });
}
