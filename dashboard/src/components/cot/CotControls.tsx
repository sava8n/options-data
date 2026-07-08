import type { CotWindow } from '../../api/client';
import { COT_WINDOWS } from './windows';

const FLOW_WEEKS = [12, 26, 52];

interface Props {
  window: CotWindow;
  flowWeeks: number;
  onWindow: (w: CotWindow) => void;
  onFlowWeeks: (n: number) => void;
}

export default function CotControls({ window, flowWeeks, onWindow, onFlowWeeks }: Props) {
  return (
    <div className="cot-controls">
      <label className="expiry">
        <span className="expiry__label">INDEX WINDOW</span>
        <select
          className="expiry__select"
          value={window}
          onChange={(e) => onWindow(Number(e.target.value) as CotWindow)}
        >
          {COT_WINDOWS.map(({ value, label }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>

      <label className="expiry">
        <span className="expiry__label">FLOW LOOKBACK</span>
        <select
          className="expiry__select"
          value={flowWeeks}
          onChange={(e) => onFlowWeeks(Number(e.target.value))}
        >
          {FLOW_WEEKS.map((n) => (
            <option key={n} value={n}>
              {n}W
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
