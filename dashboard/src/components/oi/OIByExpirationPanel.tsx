import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type {
  OIByExpirationPoint,
  OIByExpirationResponse,
} from '../../types';
import { expiryLabel } from '../../utils/format';

const GRID = '#243133';
const AXIS_LINE = '#3a4a4d';
const LABEL = '#ffb000';
const MONO = 'monospace';

// calls = teal, puts = amber; ITM brighter, OTM deeper.
const SERIES = [
  { key: 'itm_calls', name: 'ITM Calls', color: '#5fded0', stack: 'calls' },
  { key: 'otm_calls', name: 'OTM Calls', color: '#178f80', stack: 'calls' },
  { key: 'itm_puts', name: 'ITM Puts', color: '#ffcf4d', stack: 'puts' },
  { key: 'otm_puts', name: 'OTM Puts', color: '#c8860b', stack: 'puts' },
] as const satisfies ReadonlyArray<{
  key: keyof OIByExpirationPoint;
  name: string;
  color: string;
  stack: string;
}>;

// open interest (contracts): 62000 -> "62k".
const oiFmt = (v: number) =>
  v >= 1000
    ? `${(v / 1000).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`
    : `${Math.round(v)}`;

export default function OIByExpirationPanel({
  data,
}: {
  data: OIByExpirationResponse;
}) {
  const option = useMemo<EChartsOption>(() => {
    // one stacked bar per expiry, near-dated first.
    const rows = [...data.points].sort((a, b) => a.tte_years - b.tte_years);
    const labels = rows.map((p) => expiryLabel(p.expiry));

    const axisLabelStyle = { color: LABEL, fontFamily: MONO, fontSize: 11 };
    const nameStyle = { color: LABEL, fontFamily: MONO, fontSize: 13 };

    const opt = {
      backgroundColor: 'transparent',
      legend: {
        data: SERIES.map((s) => s.name),
        top: 4,
        itemWidth: 10,
        itemHeight: 10,
        textStyle: { color: LABEL, fontFamily: MONO, fontSize: 11 },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#0b0e10',
        borderColor: GRID,
        borderWidth: 1,
        textStyle: { color: LABEL, fontFamily: MONO, fontSize: 12 },
        valueFormatter: (v: number | string) => oiFmt(Number(v)),
      },
      grid: { left: 56, right: 18, top: 40, bottom: 60 },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, rotate: 45, interval: 0 },
      },
      yAxis: {
        type: 'value',
        name: 'OI',
        nameGap: 12,
        nameTextStyle: nameStyle,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: oiFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
      series: SERIES.map((s) => ({
        type: 'bar',
        name: s.name,
        stack: s.stack,
        barMaxWidth: 28,
        data: rows.map((p) => p[s.key]),
        itemStyle: { color: s.color },
        emphasis: { focus: 'series' },
      })),
    };

    return opt as unknown as EChartsOption;
  }, [data]);

  return (
    <ReactECharts
      option={option}
      notMerge
      lazyUpdate
      style={{ width: '100%', height: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  );
}
