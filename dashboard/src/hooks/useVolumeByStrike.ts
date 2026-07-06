import { useQuery } from '@tanstack/react-query';
import { fetchVolumeByStrike } from '../api/client';

export function useVolumeByStrike(currency = 'BTC') {
  return useQuery({
    queryKey: ['volume-strike', currency],
    queryFn: () => fetchVolumeByStrike(currency),
  });
}
