import { useState } from 'react';

import { useSettings } from '../../settings/store';

export interface DteWindow {
  min: number;
  max: number;
}

// section-local DTE window, re-seeded from the settings default whenever that default moves
export function useDteWindow() {
  const { minDte, maxDte } = useSettings();
  const [dte, setDte] = useState<DteWindow>({ min: minDte, max: maxDte });
  const [seed, setSeed] = useState({ minDte, maxDte });

  // the default moved, so drop the section-local override
  if (seed.minDte !== minDte || seed.maxDte !== maxDte) {
    setSeed({ minDte, maxDte });
    setDte({ min: minDte, max: maxDte });
  }

  return [dte, setDte] as const;
}
