import { useQuery } from '@tanstack/react-query';
import { fetchCotHistory } from '../api/client';

export function useCotHistory() {
  return useQuery({
    queryKey: ['cot-history'],
    queryFn: () => fetchCotHistory(),
  });
}
