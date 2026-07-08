import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { fetchCotIndex, type CotWindow } from '../api/client';

export function useCotIndex(window: CotWindow) {
  return useQuery({
    queryKey: ['cot-index', window],
    queryFn: () => fetchCotIndex(window),
    // keep the chart populated while switching window
    placeholderData: keepPreviousData,
  });
}
