import { useState } from 'react';

import type { CotWindow } from '../../api/client';
import CotControls from './CotControls';
import CotFlowSection from './CotFlowSection';
import CotIndexSection from './CotIndexSection';
import CotNetHistorySection from './CotNetHistorySection';
import CotReportSection from './CotReportSection';

export default function CotTab() {
  const [window, setWindow] = useState<CotWindow>(156);
  const [flowWeeks, setFlowWeeks] = useState(26);

  return (
    <>
      <CotControls
        window={window}
        flowWeeks={flowWeeks}
        onWindow={setWindow}
        onFlowWeeks={setFlowWeeks}
      />
      <CotReportSection window={window} />
      <div className="panels">
        <CotFlowSection weeks={flowWeeks} />
        <CotIndexSection window={window} />
      </div>
      <CotNetHistorySection />
    </>
  );
}
