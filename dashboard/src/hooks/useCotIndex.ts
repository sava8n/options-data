import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { fetchCotIndex, type CotMethod, type CotWindow } from '../api/client';

export function useCotIndex(currency = 'BTC', window: CotWindow = 52, method: CotMethod = 'rank') {
  return useQuery({
    queryKey: ['cot-index', currency, window, method],
    queryFn: () => fetchCotIndex(currency, window, method),
    // keep the chart populated while switching window
    placeholderData: keepPreviousData,
  });
}
