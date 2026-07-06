import { useQuery } from '@tanstack/react-query';
import { fetchSpotHistory } from '../api/client';

export function useSpotHistory(currency = 'BTC') {
  return useQuery({
    queryKey: ['spot-history', currency],
    queryFn: () => fetchSpotHistory(currency),
  });
}
