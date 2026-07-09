import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

import type { ProbCurvesResponse } from '../../types';
import { expiryLabel, ivFmt, strikeFmt } from '../../utils/format';
import {
  AMBER,
  AXIS_LINE,
  GRID,
  MONO,
  PALETTE,
  TEXT,
  ZERO,
  axisLabelStyle,
  axisNameStyle,
  tooltipStyle,
} from '../../theme/charts';

interface ExpiryCurve {
  label: string;
  tte: number;
  points: [number, number][]; // [strike, prob], ascending by strike
}

export default function ProbCurvesPanel({ data }: { data: ProbCurvesResponse }) {
  const option = useMemo<EChartsOption>(() => {
    // group quotes by expiry, then build one probability curve (P(S>K) vs strike) per expiry
    const byExpiry = new Map<string, { tte: number; strikes: Map<number, number[]> }>();
    for (const p of data.points) {
      let row = byExpiry.get(p.expiry);
      if (!row) {
        row = { tte: p.tte_years, strikes: new Map() };
        byExpiry.set(p.expiry, row);
      }
      const probs = row.strikes.get(p.strike);
      if (probs) probs.push(p.prob_above);
      else row.strikes.set(p.strike, [p.prob_above]);
    }

    const curves: ExpiryCurve[] = [...byExpiry.entries()]
      .map(([iso, row]) => {
        // ascending strikes; average where a call and a put share a strike
        const points = [...row.strikes.entries()]
          .sort((a, b) => a[0] - b[0])
          .map(([strike, probs]) => [
            strike,
            probs.reduce((s, v) => s + v, 0) / probs.length,
          ] as [number, number]);
        return { label: expiryLabel(iso), tte: row.tte, points };
      })
      .sort((a, b) => a.tte - b.tte); // near-dated first, so legend/z-order is chronological

    const opt = {
      backgroundColor: 'transparent',
      color: PALETTE,
      tooltip: {
        ...tooltipStyle,
        trigger: 'item',
        formatter: (p: { seriesName?: string; value?: number[] }) => {
          const arr = p.value ?? [];
          if (arr.length < 2) return '';
          const [k, prob] = arr;
          return `${p.seriesName}<br/>K ${k.toLocaleString('en-US')}<br/>P ${(prob * 100).toFixed(1)}%`;
        },
      },
      legend: {
        type: 'scroll',
        top: 6,
        left: 10,
        right: 10,
        itemWidth: 18,
        itemHeight: 2,
        itemGap: 12,
        textStyle: { color: TEXT, fontFamily: MONO, fontSize: 10 },
        pageTextStyle: { color: AMBER, fontFamily: MONO },
        pageIconColor: AMBER,
        pageIconInactiveColor: AXIS_LINE,
        data: curves.map((c) => c.label),
      },
      grid: { left: 56, right: 18, top: 66, bottom: 44 },
      xAxis: {
        type: 'value',
        name: 'STRIKE',
        nameLocation: 'middle',
        nameGap: 28,
        nameTextStyle: axisNameStyle,
        scale: true,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: strikeFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
      yAxis: {
        type: 'value',
        name: 'P(S>K)',
        nameGap: 12,
        nameTextStyle: axisNameStyle,
        min: 0,
        max: 1,
        axisLine: { lineStyle: { color: AXIS_LINE } },
        axisTick: { lineStyle: { color: AXIS_LINE } },
        axisLabel: { ...axisLabelStyle, formatter: ivFmt },
        splitLine: { lineStyle: { color: GRID } },
      },
      series: curves.map((c, i) => ({
        type: 'line',
        name: c.label,
        data: c.points,
        showSymbol: true,
        symbol: 'circle',
        symbolSize: 4,
        smooth: true,
        lineStyle: { width: 1.5 },
        emphasis: { focus: 'series', lineStyle: { width: 3 } },
        ...(i === 0 && {
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { color: ZERO, type: 'dashed', width: 1 },
            label: {
              color: ZERO,
              fontFamily: MONO,
              fontSize: 10,
              formatter: 'SPOT',
            },
            data: [{ xAxis: data.spot }],
          },
        }),
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
