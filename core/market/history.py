"""Incremental daily-candle history.

Closed daily candles are immutable, so a refresh only needs the window since the
last stored candle: the running candle is replaced, new ones appended, and the
series trimmed to the trailing year.
"""

from __future__ import annotations

import math
import time

WINDOW_DAYS = 365
_DAY_MS = 86_400_000

_TV_ARRAYS = ("ticks", "open", "high", "low", "close", "volume")


def refresh_days(last_tick_ms: int | None) -> int:
    """Fetch window covering everything since the last stored candle (min 2 days)."""
    if last_tick_ms is None:
        return WINDOW_DAYS
    elapsed = (time.time() * 1000 - last_tick_ms) / _DAY_MS
    return min(WINDOW_DAYS, max(2, math.ceil(elapsed) + 1))


def spot_last_tick(candles: dict | None) -> int | None:
    """Open time (ms) of the last stored TradingView-format candle."""
    if candles and candles.get("status") == "ok" and candles.get("ticks"):
        return int(candles["ticks"][-1])
    return None


def splice_spot(prev: dict | None, fresh: dict) -> dict:
    """Merge TradingView-format arrays ``{ticks, open, …}``: fresh replaces overlap."""
    if not prev or prev.get("status") != "ok":
        return fresh
    if fresh.get("status") != "ok" or not fresh.get("ticks"):
        return prev
    since = fresh["ticks"][0]
    keep = sum(1 for t in prev["ticks"] if t < since)
    merged: dict = {"status": "ok"}
    for key in _TV_ARRAYS:
        merged[key] = (list(prev.get(key, []))[:keep] + list(fresh.get(key, [])))[-WINDOW_DAYS:]
    return merged


def dvol_last_tick(candles: list | None) -> int | None:
    """Open time (ms) of the last stored DVOL candle."""
    return int(candles[-1][0]) if candles else None


def splice_dvol(prev: list | None, fresh: list) -> list:
    """Merge ``[[ts, o, h, l, c], …]`` candles: fresh replaces overlap."""
    if not prev:
        return fresh
    if not fresh:
        return prev
    since = fresh[0][0]
    kept = [c for c in prev if c[0] < since]
    return (kept + fresh)[-WINDOW_DAYS:]
