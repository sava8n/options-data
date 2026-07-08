import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { fetchCotReport, type CotWindow } from '../api/client';

export function useCotReport(window: CotWindow) {
  return useQuery({
    queryKey: ['cot-report', window],
    queryFn: () => fetchCotReport(window),
    // keep the table populated while switching window
    placeholderData: keepPreviousData,
  });
}
