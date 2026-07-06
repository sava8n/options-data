import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type { VolumeByStrikeResponse } from '../../types';
import { oiFmt, strikeFmt } from '../../utils/format';
import {
  AXIS_LINE,
  CALL,
  GRID,
  PUT,
  axisLabelStyle,
  axisNameStyle,
  tooltipStyle,
} from '../../theme/charts';

export default function VolumeByStrikePanel({ data }: { data: VolumeByStrikeResponse }) {
  const option = useMemo<EChartsOption>(() => {
    const rows = [...data.points].sort((a, b) => a.strike - b.strike);
    const labels = rows.map((p) => strikeFmt(p.strike));

    const opt = {
      backgroundColor: 'transparent',
      legend: {
        data: ['Call Volume', 'Put Volume'],
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
        axisLabel: { ...axisLabelStyle, rotate: 45, interval: 'auto' },
      },
      yAxis: {
        type: 'value',
        name: 'VOL 24H',
        nameGap: 12,
        nameTextStyle: axisNameStyle,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: oiFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
      series: [
        {
          type: 'bar',
          name: 'Call Volume',
          barMaxWidth: 22,
          data: rows.map((p) => p.call_volume),
          itemStyle: { color: CALL },
          emphasis: { focus: 'series' },
        },
        {
          type: 'bar',
          name: 'Put Volume',
          barMaxWidth: 22,
          data: rows.map((p) => p.put_volume),
          itemStyle: { color: PUT },
          emphasis: { focus: 'series' },
        },
      ],
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
