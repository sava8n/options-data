import { useQuery } from '@tanstack/react-query';
import { fetchOIByExpiration } from '../api/client';

export function useOIByExpiration(currency = 'BTC') {
  return useQuery({
    queryKey: ['oi-expiration', currency],
    queryFn: () => fetchOIByExpiration(currency),
  });
}
