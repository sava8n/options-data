"""Incremental candle history: refresh window, last-tick reads and overlap-aware splicing."""

from __future__ import annotations

import market.history as history
from market.history import (
    WINDOW_DAYS,
    _DAY_MS,
    dvol_last_tick,
    refresh_days,
    spot_last_tick,
    splice_dvol,
    splice_spot,
)


def test_refresh_days_none_is_full_window():
    assert refresh_days(None) == WINDOW_DAYS


def test_refresh_days_from_elapsed(monkeypatch):
    now_ms = 2_000_000_000_000
    monkeypatch.setattr(history.time, "time", lambda: now_ms / 1000.0)
    assert refresh_days(now_ms - 5 * _DAY_MS) == 6            # ceil(5) + 1
    assert refresh_days(now_ms - 400 * _DAY_MS) == WINDOW_DAYS  # capped at the window
    assert refresh_days(int(now_ms - 0.5 * _DAY_MS)) == 2      # floored at 2


def test_spot_last_tick():
    assert spot_last_tick({"status": "ok", "ticks": [1, 2, 3]}) == 3
    assert spot_last_tick({"status": "error", "ticks": [1]}) is None
    assert spot_last_tick(None) is None


def test_splice_spot_no_prev_returns_fresh():
    fresh = {"status": "ok", "ticks": [2, 3], "close": [20.0, 30.0]}
    assert splice_spot(None, fresh) is fresh


def test_splice_spot_overlap_replaced_by_fresh():
    prev = {"status": "ok", "ticks": [1, 2], "open": [0, 0], "high": [0, 0], "low": [0, 0], "close": [10.0, 15.0], "volume": [0, 0]}
    fresh = {"status": "ok", "ticks": [2, 3], "open": [1, 1], "high": [1, 1], "low": [1, 1], "close": [20.0, 30.0], "volume": [1, 1]}
    out = splice_spot(prev, fresh)
    assert out["ticks"] == [1, 2, 3]
    assert out["close"] == [10.0, 20.0, 30.0]  # the overlapping tick 2 takes the fresh close


def test_splice_spot_bad_fresh_returns_prev():
    prev = {"status": "ok", "ticks": [1], "close": [10.0]}
    assert splice_spot(prev, {"status": "error"}) is prev


def test_dvol_last_tick_and_splice():
    assert dvol_last_tick([[1, 0, 0, 0, 0], [2, 0, 0, 0, 0]]) == 2
    assert dvol_last_tick(None) is None

    prev = [[1, 0, 0, 0, 10.0], [2, 0, 0, 0, 15.0]]
    fresh = [[2, 0, 0, 0, 20.0], [3, 0, 0, 0, 30.0]]
    out = splice_dvol(prev, fresh)
    assert [c[0] for c in out] == [1, 2, 3]
    assert out[1][4] == 20.0  # overlapping tick 2 replaced by fresh
