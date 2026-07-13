import { useEffect, useMemo, useRef } from 'react';
import {
  CandlestickSeries,
  ColorType,
  LineStyle,
  createChart,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
} from 'lightweight-charts';

import type { SpotCandle } from '../../types';
import type { PriceLevel, QuantileBand } from './levels';
import { QuantileBandPrimitive } from './QuantileBandPrimitive';
import { AMBER, AXIS_LINE, GRID, MONO } from '../../theme/charts';
import { SPOT_CHART_LOOKBACK_DAYS } from '../../config';

const UP = '#33ff66';
const DOWN = '#ff3b30';

interface Props {
  candles: SpotCandle[];
  levels: PriceLevel[];
  band?: QuantileBand;
}

export default function SpotHistoryPanel({ candles, levels, band }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const bandRef = useRef<QuantileBandPrimitive | null>(null);
  const priceLinesRef = useRef<IPriceLine[]>([]);
  const windowedRef = useRef(false);

  const rows = useMemo(
    () =>
      candles.map((c) => ({
        time: c.ts.slice(0, 10), // daily candles: 'YYYY-MM-DD'
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      })),
    [candles],
  );

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: AMBER,
        fontFamily: MONO,
        fontSize: 11,
      },
      grid: {
        vertLines: { color: GRID },
        horzLines: { color: GRID },
      },
      rightPriceScale: {
        borderColor: AXIS_LINE,
        // tight auto-fit: let the visible candles use almost the full panel height
        scaleMargins: { top: 0.05, bottom: 0.05 },
      },
      timeScale: { borderColor: AXIS_LINE },
      crosshair: {
        vertLine: { color: AXIS_LINE, labelBackgroundColor: '#0b0e10' },
        horzLine: { color: AXIS_LINE, labelBackgroundColor: '#0b0e10' },
      },
      localization: {
        priceFormatter: (p: number) => p.toLocaleString('en-US', { maximumFractionDigits: 0 }),
      },
    });
    const series = chart.addSeries(CandlestickSeries, {
      upColor: UP,
      downColor: DOWN,
      wickUpColor: UP,
      wickDownColor: DOWN,
      borderVisible: false,
    });

    const bandPrimitive = new QuantileBandPrimitive();
    series.attachPrimitive(bandPrimitive);

    chartRef.current = chart;
    seriesRef.current = series;
    bandRef.current = bandPrimitive;
    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
      bandRef.current = null;
      priceLinesRef.current = [];
      windowedRef.current = false;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    const series = seriesRef.current;
    if (!chart || !series) return;
    series.setData(rows);
    // default view on first load; later refetches keep the user's zoom/pan
    if (!windowedRef.current) {
      chart.timeScale().setVisibleLogicalRange({
        from: Math.max(0, rows.length - SPOT_CHART_LOOKBACK_DAYS),
        to: rows.length,
      });
      windowedRef.current = true;
    }
  }, [rows]);

  // options-derived levels as horizontal price lines, resynced on each refetch
  useEffect(() => {
    const series = seriesRef.current;
    if (!series) return;
    priceLinesRef.current.forEach((line) => series.removePriceLine(line));
    priceLinesRef.current = levels.map((lvl) =>
      series.createPriceLine({
        price: lvl.price,
        color: lvl.color,
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: lvl.title,
      }),
    );
  }, [levels]);

  // implied quantile band as a background rectangle behind the candles
  useEffect(() => {
    bandRef.current?.setBand(band ?? null);
  }, [band]);

  return <div ref={containerRef} />;
}
