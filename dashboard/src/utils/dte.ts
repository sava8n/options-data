// window an OTM point list by days-to-expiry (points carry tte_years)
export function filterByDTE<T extends { tte_years: number }>(
  points: T[],
  minDte: number,
  maxDte: number,
): T[] {
  const min = minDte / 365.25;
  const max = maxDte / 365.25;
  return points.filter((p) => p.tte_years >= min && p.tte_years <= max);
}
