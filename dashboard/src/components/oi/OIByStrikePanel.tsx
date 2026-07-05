import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type { OIByStrikeResponse } from '../../types';
import { oiFmt, strikeFmt, usdFull, usdShort } from '../../utils/format';
import {
  AXIS_LINE,
  GRID,
  OI_SERIES,
  axisLabelStyle,
  axisNameStyle,
  tooltipStyle,
} from '../../theme/charts';

const RED = '#ff3b30'; // intrinsic value / max pain

export default function OIByStrikePanel({ data }: { data: OIByStrikeResponse }) {
  const option = useMemo<EChartsOption>(() => {
    // one grouped calls/puts bar per strike, low strikes first.
    const rows = [...data.points].sort((a, b) => a.strike - b.strike);
    const labels = rows.map((p) => strikeFmt(p.strike));

    // max-pain analytics only exist for a single expiry.
    const hasIntrinsic = data.max_pain != null;
    const maxPainIdx = data.max_pain != null ? rows.findIndex((p) => p.strike === data.max_pain) : -1;

    const legend: string[] = OI_SERIES.map((s) => s.name);
    if (hasIntrinsic) legend.push('Total Intrinsic Value');

    const yAxis: unknown[] = [
      {
        type: 'value',
        name: 'OI',
        nameGap: 12,
        nameTextStyle: axisNameStyle,
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
        nameTextStyle: { ...axisNameStyle, color: RED },
        position: 'right',
        axisLine: { show: true, lineStyle: { color: RED } },
        axisTick: { lineStyle: { color: RED } },
        axisLabel: { ...axisLabelStyle, color: RED, formatter: usdShort },
        splitLine: { show: false },
      });
    }

    const series: unknown[] = OI_SERIES.map((s) => ({
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
            ...axisLabelStyle,
            color: RED,
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
        textStyle: axisLabelStyle,
      },
      tooltip: {
        ...tooltipStyle,
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
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
