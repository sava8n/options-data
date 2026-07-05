import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type { OIByStrikePoint, OIByStrikeResponse } from '../../types';
import { strikeFmt } from '../../utils/format';

const GRID = '#243133';
const AXIS_LINE = '#3a4a4d';
const LABEL = '#ffb000';
const RED = '#ff3b30'; // intrinsic value / max pain
const MONO = 'monospace';

// calls = teal, puts = amber; ITM brighter, OTM deeper.
const SERIES = [
  { key: 'itm_calls', name: 'ITM Calls', color: '#5fded0', stack: 'calls' },
  { key: 'otm_calls', name: 'OTM Calls', color: '#178f80', stack: 'calls' },
  { key: 'itm_puts', name: 'ITM Puts', color: '#ffcf4d', stack: 'puts' },
  { key: 'otm_puts', name: 'OTM Puts', color: '#c8860b', stack: 'puts' },
] as const satisfies ReadonlyArray<{
  key: keyof OIByStrikePoint;
  name: string;
  color: string;
  stack: string;
}>;

// open interest (contracts): 62000 -> "62k".
const oiFmt = (v: number) =>
  v >= 1000
    ? `${(v / 1000).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`
    : `${Math.round(v)}`;

// intrinsic value (USD): 12_500_000 -> "$12.5M".
const usdShort = (v: number) => {
  if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toLocaleString('en-US', { maximumFractionDigits: 1 })}B`;
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toLocaleString('en-US', { maximumFractionDigits: 1 })}M`;
  if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toLocaleString('en-US', { maximumFractionDigits: 1 })}k`;
  return `$${Math.round(v)}`;
};

// max-pain label: 61500 -> "$61,500.00".
const usdFull = (v: number) =>
  `$${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function OIByStrikePanel({ data }: { data: OIByStrikeResponse }) {
  const option = useMemo<EChartsOption>(() => {
    // one grouped calls/puts bar per strike, low strikes first.
    const rows = [...data.points].sort((a, b) => a.strike - b.strike);
    const labels = rows.map((p) => strikeFmt(p.strike));

    // max-pain analytics only exist for a single expiry.
    const hasIntrinsic = data.max_pain != null;
    const maxPainIdx = data.max_pain != null ? rows.findIndex((p) => p.strike === data.max_pain) : -1;

    const axisLabelStyle = { color: LABEL, fontFamily: MONO, fontSize: 11 };
    const nameStyle = { color: LABEL, fontFamily: MONO, fontSize: 13 };

    const legend: string[] = SERIES.map((s) => s.name);
    if (hasIntrinsic) legend.push('Total Intrinsic Value');

    const yAxis: unknown[] = [
      {
        type: 'value',
        name: 'OI',
        nameGap: 12,
        nameTextStyle: nameStyle,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: oiFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
    ];
    if (hasIntrinsic) {
      yAxis.push({
        type: 'value',
        name: 'INTRINSIC',
        nameGap: 12,
        nameTextStyle: { ...nameStyle, color: RED },
        position: 'right',
        axisLine: { show: true, lineStyle: { color: RED } },
        axisTick: { lineStyle: { color: RED } },
        axisLabel: { color: RED, fontFamily: MONO, fontSize: 11, formatter: usdShort },
        splitLine: { show: false },
      });
    }

    const series: unknown[] = SERIES.map((s) => ({
      type: 'bar',
      name: s.name,
      stack: s.stack,
      barMaxWidth: 22,
      data: rows.map((p) => p[s.key]),
      itemStyle: { color: s.color },
      emphasis: { focus: 'series' },
    }));

    if (hasIntrinsic) {
      series.push({
        type: 'scatter',
        name: 'Total Intrinsic Value',
        yAxisIndex: 1,
        symbolSize: 6,
        // flat scalar array: index -> strike category, value -> intrinsic (USD).
        data: rows.map((p) => p.intrinsic_value ?? 0),
        itemStyle: { color: RED },
        // vertical dashed line at the max-pain strike.
        markLine: {
          symbol: 'none',
          silent: true,
          lineStyle: { color: RED, type: 'dashed', width: 1 },
          label: {
            color: RED,
            fontFamily: MONO,
            fontSize: 11,
            formatter: () => `Max Pain ${usdFull(data.max_pain as number)}`,
          },
          data: [{ xAxis: maxPainIdx }],
        },
      });
    }

    const opt = {
      backgroundColor: 'transparent',
      legend: {
        data: legend,
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
        valueFormatter: (v: number | string) => {
          // heuristic: large magnitudes are intrinsic-value dollars, else contracts.
          const n = Number(v);
          return Math.abs(n) >= 100000 ? usdShort(n) : oiFmt(n);
        },
      },
      grid: { left: 56, right: hasIntrinsic ? 64 : 18, top: 40, bottom: 60 },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, rotate: 45, interval: 'auto' },
      },
      yAxis,
      series,
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
