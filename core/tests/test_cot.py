"""COT transforms: coercion, normalize, aggregate, deltas, index, prices and report."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cot.aggregate import build as aggregate
from cot.deltas import build as deltas
from cot.fields import CATEGORIES
from cot.index import MIN_PERIODS, build as build_index
from cot.normalize import build as normalize
from cot.prices import align, splice
from cot.report import build as build_report
from cot.values import opt_float, opt_int


def _records(dates, codes):
    rows = []
    for d in dates:
        for code in codes:
            rows.append(
                {
                    "report_date_as_yyyy_mm_dd": d,
                    "cftc_contract_market_code": code,
                    "open_interest_all": "1000",
                    "dealer_positions_long_all": "100",
                    "dealer_positions_short_all": "60",
                    "dealer_positions_spread_all": "10",
                }
            )
    return rows


# ---- values ----

def test_opt_float_and_opt_int():
    assert opt_float(None) is None
    assert opt_float(float("nan")) is None
    assert opt_float("3.5") == 3.5
    assert opt_int(None) is None
    assert opt_int(np.nan) is None
    assert opt_int(4.9) == 4


# ---- normalize ----

def test_normalize_raises_on_empty():
    with pytest.raises(ValueError):
        normalize([])


def test_normalize_raises_on_missing_key():
    with pytest.raises(ValueError):
        normalize([{"foo": "bar"}])


def test_normalize_dedupes_report_date_and_code():
    records = _records(["2026-06-03"], ["133741"]) * 1
    records = [dict(records[0]), dict(records[0])]  # two independent duplicate rows
    tidy = normalize(records)
    assert len(tidy) == 1


def test_normalize_absent_traders_stay_nan_present_positions_filled():
    tidy = normalize(_records(["2026-06-03"], ["133741"]))
    assert tidy["dealer_long"].iloc[0] == 100.0
    # non-reportables have no trader series in the report -> structurally NaN
    assert pd.isna(tidy["traders_nonrept_long"].iloc[0])


# ---- aggregate ----

def test_aggregate_weights_to_coin_equivalent():
    tidy = normalize(_records(["2026-06-03"], ["133741", "133742"]))
    agg = aggregate(tidy, {"133741": 5.0, "133742": 0.1})
    # dealer_long = 100 * 5 + 100 * 0.1 = 510; oi = 1000 * 5 + 1000 * 0.1 = 5100
    assert agg["dealer_long"].iloc[0] == pytest.approx(510.0)
    assert agg["oi"].iloc[0] == pytest.approx(5100.0)


# ---- deltas ----

def test_deltas_net_and_report_over_report_diff():
    tidy = normalize(_records(["2026-06-03", "2026-06-10"], ["133741"]))
    out = deltas(aggregate(tidy, {"133741": 1.0}))
    assert (out["dealer_net"] == 40.0).all()  # long 100 - short 60
    assert pd.isna(out["dealer_delta"].iloc[0])  # first row has no prior
    assert out["dealer_delta"].iloc[1] == 0.0


# ---- index ----

def _rising_history():
    dates = pd.date_range("2020-01-07", periods=60, freq="7D")
    net = np.arange(60, dtype="float64")
    return pd.DataFrame({f"{cat}_net": net for cat in CATEGORIES}, index=dates)


def test_index_rank_respects_min_periods_and_scales_to_100():
    idx = build_index(_rising_history(), window=0, method="rank")
    assert idx["dealer"].iloc[: MIN_PERIODS - 1].isna().all()  # before a year of history
    assert idx["dealer"].iloc[-1] == pytest.approx(100.0)  # latest is the window max


def test_index_minmax_flat_range_is_nan():
    dates = pd.date_range("2020-01-07", periods=60, freq="7D")
    flat = pd.DataFrame({f"{cat}_net": np.full(60, 5.0) for cat in CATEGORIES}, index=dates)
    idx = build_index(flat, window=0, method="minmax")
    assert idx["dealer"].isna().all()


# ---- prices ----

def test_splice_freshest_close_wins():
    prev = {"status": "ok", "ticks": [1, 2], "close": [10.0, 20.0]}
    fresh = {"status": "ok", "ticks": [2, 3], "close": [25.0, 30.0]}
    out = splice(prev, [fresh])
    assert out["ticks"] == [1, 2, 3]
    assert out["close"] == [10.0, 25.0, 30.0]  # tick 2 replaced by the fresher chunk


def test_splice_filters_non_ok_status():
    assert splice(None, [{"status": "error"}]) is None


def test_align_maps_report_date_to_its_day_close():
    day = 86_400_000
    candles = {"status": "ok", "ticks": [0, 7 * day, 14 * day], "close": [10.0, 20.0, 30.0]}
    report_dates = pd.to_datetime(["1970-01-08", "1970-01-15"])  # day 7 and day 14
    aligned = align(candles, report_dates)
    assert list(aligned.values) == [20.0, 30.0]


def test_align_before_first_candle_is_nan():
    candles = {"status": "ok", "ticks": [10 * 86_400_000], "close": [10.0]}
    aligned = align(candles, pd.to_datetime(["1970-01-05"]))
    assert pd.isna(aligned.iloc[0])


# ---- report ----

def test_report_build_is_deterministic():
    tidy = normalize(_records(["2026-06-03", "2026-06-10"], ["133741"]))
    history = deltas(aggregate(tidy, {"133741": 1.0}))
    index = build_index(history, window=0, method="rank")
    prices = pd.Series([np.nan, 30_000.0], index=history.index)

    payload = build_report(history, index, prices, now=pd.Timestamp("2026-06-15"))
    assert payload["oi"] == 1000.0
    assert payload["price"] == 30_000.0
    assert payload["oi_usd"] == pytest.approx(1000.0 * 30_000.0)

    dealer = next(row for row in payload["rows"] if row["category"] == "dealer")
    assert dealer["net"] == 40.0
    # net unchanged week-over-week -> delta 0 over prev_net 40 -> 0%
    assert dealer["delta_net_pct"] == pytest.approx(0.0)
    # index needs a year of history; two rows -> None
    assert dealer["index"] is None
