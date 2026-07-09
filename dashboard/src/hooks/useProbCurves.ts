import { useQuery } from '@tanstack/react-query';
import { fetchProbCurves } from '../api/client';

export function useProbCurves(currency = 'BTC') {
  return useQuery({
    queryKey: ['prob-curves', currency],
    queryFn: () => fetchProbCurves(currency),
  });
}
