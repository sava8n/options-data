import { useQuery } from '@tanstack/react-query';
import { fetchSpot } from '../api/client';

export function useSpot(currency = 'BTC') {
  return useQuery({
    queryKey: ['spot', currency],
    queryFn: () => fetchSpot(currency),
  });
}
