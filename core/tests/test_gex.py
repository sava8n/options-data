"""Dollar-gamma exposure by strike and the zero-gamma flip level."""

from __future__ import annotations

import pandas as pd
import pytest

from gex.by_strike import GEX_COLUMNS, build, flip_level

_EXPIRY = pd.Timestamp("2035-01-31", tz="UTC")


def _greeks(strikes, gammas):
    return pd.DataFrame({"expiry": [_EXPIRY] * len(strikes), "strike": strikes, "gamma": gammas})


def _oi(strikes, option_types, ois, forward):
    return pd.DataFrame(
        {
            "expiry": [_EXPIRY] * len(strikes),
            "strike": strikes,
            "option_type": option_types,
            "open_interest": ois,
            "forward": [forward] * len(strikes),
        }
    )


def test_build_dollar_gamma_and_signs():
    greeks = _greeks([90.0, 110.0], [0.001, 0.002])
    oi = _oi([90.0, 110.0], ["P", "C"], [10.0, 5.0], forward=100.0)
    out = build(greeks, oi)
    assert list(out.columns) == GEX_COLUMNS

    # put at 90: dollar = 10 * 0.001 * 100^2 * 0.01 = 1.0, signed negative
    put_row = out[out["strike"] == 90.0].iloc[0]
    assert put_row["put_gex"] == pytest.approx(-1.0)
    assert put_row["call_gex"] == pytest.approx(0.0)

    # call at 110: dollar = 5 * 0.002 * 100^2 * 0.01 = 1.0, signed positive
    call_row = out[out["strike"] == 110.0].iloc[0]
    assert call_row["call_gex"] == pytest.approx(1.0)
    assert call_row["net_gex"] == pytest.approx(1.0)


def test_build_empty_inputs_typed():
    empty_greeks = pd.DataFrame({"expiry": [], "strike": [], "gamma": []})
    empty_oi = pd.DataFrame(
        {"expiry": [], "strike": [], "option_type": [], "open_interest": [], "forward": []}
    )
    out = build(empty_greeks, empty_oi)
    assert out.empty
    assert list(out.columns) == GEX_COLUMNS


def test_flip_level_single_crossing():
    per_strike = pd.DataFrame({"strike": [90.0, 100.0, 110.0], "net_gex": [-2.0, -1.0, 5.0]})
    # cumulative net-GEX = [-2, -3, 2]; sign flips between strikes 100 and 110
    # frac = -3 / (-3 - 2) = 0.6 -> 100 + 0.6 * 10 = 106
    assert flip_level(per_strike, spot=100.0) == pytest.approx(106.0)


def test_flip_level_picks_crossing_nearest_spot():
    per_strike = pd.DataFrame(
        {"strike": [80.0, 90.0, 100.0, 110.0], "net_gex": [3.0, -6.0, 6.0, -6.0]}
    )
    # cumulative = [3, -3, 3, -3]; crossings at 85, 95, 105 -> nearest to spot 101 is 105
    assert flip_level(per_strike, spot=101.0) == pytest.approx(105.0)


def test_flip_level_no_crossing_returns_none():
    per_strike = pd.DataFrame({"strike": [90.0, 100.0], "net_gex": [1.0, 2.0]})  # cum = [1, 3]
    assert flip_level(per_strike, spot=95.0) is None


def test_flip_level_too_few_rows_returns_none():
    per_strike = pd.DataFrame({"strike": [100.0], "net_gex": [1.0]})
    assert flip_level(per_strike, spot=100.0) is None
