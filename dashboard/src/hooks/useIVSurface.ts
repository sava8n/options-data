import { useQuery } from '@tanstack/react-query';
import { fetchIVSurface } from '../api/client';

export function useIVSurface(currency = 'BTC') {
  return useQuery({
    queryKey: ['iv-surface', currency],
    queryFn: () => fetchIVSurface(currency),
  });
}
