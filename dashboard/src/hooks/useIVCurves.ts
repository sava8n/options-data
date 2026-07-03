import { useQuery } from '@tanstack/react-query';
import { fetchIVCurves } from '../api/client';

export function useIVCurves(currency = 'BTC') {
  return useQuery({
    queryKey: ['iv-curves', currency],
    queryFn: () => fetchIVCurves(currency),
  });
}
