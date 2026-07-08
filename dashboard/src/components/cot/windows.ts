import type { CotWindow } from '../../api/client';

// index windows in weeks, 0 = full history
export const COT_WINDOWS: { value: CotWindow; label: string }[] = [
  { value: 52, label: '1Y' },
  { value: 156, label: '3Y' },
  { value: 260, label: '5Y' },
  { value: 0, label: 'ALL' },
];

export function windowLabel(window: number): string {
  return COT_WINDOWS.find((w) => w.value === window)?.label ?? `${window}W`;
}
