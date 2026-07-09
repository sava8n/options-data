import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { fetchCotReport, type CotMethod, type CotWindow } from '../api/client';

export function useCotReport(currency = 'BTC', window: CotWindow = 52, method: CotMethod = 'rank') {
  return useQuery({
    queryKey: ['cot-report', currency, window, method],
    queryFn: () => fetchCotReport(currency, window, method),
    // keep the table populated while switching window
    placeholderData: keepPreviousData,
  });
}
