import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type { OIByExpirationResponse } from '../../types';
import { expiryLabel, oiFmt } from '../../utils/format';
import {
  AXIS_LINE,
  GRID,
  OI_SERIES,
  axisLabelStyle,
  axisNameStyle,
  tooltipStyle,
} from '../../theme/charts';

export default function OIByExpirationPanel({
  data,
}: {
  data: OIByExpirationResponse;
}) {
  const option = useMemo<EChartsOption>(() => {
    // one stacked bar per expiry, near-dated first.
    const rows = [...data.points].sort((a, b) => a.tte_years - b.tte_years);
    const labels = rows.map((p) => expiryLabel(p.expiry));

    const opt = {
      backgroundColor: 'transparent',
      legend: {
        data: OI_SERIES.map((s) => s.name),
        top: 4,
        itemWidth: 10,
        itemHeight: 10,
        textStyle: axisLabelStyle,
      },
      tooltip: {
        ...tooltipStyle,
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
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
        nameTextStyle: axisNameStyle,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: oiFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
      series: OI_SERIES.map((s) => ({
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
