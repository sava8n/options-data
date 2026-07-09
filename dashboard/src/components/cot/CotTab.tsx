import { useState } from 'react';

import type { CotMethod, CotWindow } from '../../api/client';
import CotControls from './CotControls';
import CotFlowSection from './CotFlowSection';
import CotIndexSection from './CotIndexSection';
import CotNetHistorySection from './CotNetHistorySection';
import CotReportSection from './CotReportSection';

export default function CotTab({ currency }: { currency: string }) {
  const [window, setWindow] = useState<CotWindow>(52);
  const [method, setMethod] = useState<CotMethod>('rank');
  const [flowWeeks, setFlowWeeks] = useState(12);

  return (
    <>
      <CotControls
        window={window}
        method={method}
        flowWeeks={flowWeeks}
        onWindow={setWindow}
        onMethod={setMethod}
        onFlowWeeks={setFlowWeeks}
      />
      <CotReportSection currency={currency} window={window} method={method} />
      <div className="panels">
        <CotFlowSection currency={currency} weeks={flowWeeks} />
        <CotIndexSection currency={currency} window={window} method={method} />
      </div>
      <CotNetHistorySection currency={currency} />
    </>
  );
}
