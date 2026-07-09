import { useQuery } from '@tanstack/react-query';
import { fetchCotHistory } from '../api/client';

export function useCotHistory(currency = 'BTC') {
  return useQuery({
    queryKey: ['cot-history', currency],
    queryFn: () => fetchCotHistory(currency),
  });
}
