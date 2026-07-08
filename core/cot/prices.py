"""Align daily close candles to COT report dates (last close on or before each report Tuesday)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def align(candles: dict | None, report_dates: pd.Index) -> pd.Series:
    if not candles or candles.get("status") != "ok" or not candles.get("ticks"):
        return pd.Series(float("nan"), index=report_dates, dtype="float64")
    closes = pd.Series(
        [float(c) for c in candles["close"]],
        index=pd.to_datetime(candles["ticks"], unit="ms"),
    ).sort_index()
    closes = closes[~closes.index.duplicated(keep="last")]
    # candle timestamps are day-opens, so the tick on the report date is that day's close
    pos = closes.index.searchsorted(report_dates, side="right") - 1
    values = np.where(pos >= 0, closes.to_numpy()[np.maximum(pos, 0)], np.nan)
    return pd.Series(values, index=report_dates, dtype="float64")
