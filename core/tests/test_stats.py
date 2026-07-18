"""Vol statistics: DVOL level/rank, realized vol and constant-maturity ATM IV."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from stats.dvol import dvol_stats
from stats.iv30 import atm_iv_at
from stats.realized import realized_vol


def _candle(close):
    return [0, 0, 0, 0, close]  # only index 4 (close) is read


def test_dvol_stats_decimal_and_rank():
    dvol, rank = dvol_stats([_candle(40.0), _candle(60.0), _candle(50.0)])
    assert dvol == pytest.approx(0.50)  # last close 50 / 100
    assert rank == pytest.approx((50.0 - 40.0) / (60.0 - 40.0))


def test_dvol_stats_flat_window_rank_none():
    dvol, rank = dvol_stats([_candle(50.0), _candle(50.0)])
    assert dvol == pytest.approx(0.50)
    assert rank is None


def test_dvol_stats_empty_returns_none_pair():
    assert dvol_stats([]) == (None, None)


def test_realized_vol_constant_prices_is_zero():
    assert realized_vol([100.0] * 10) == pytest.approx(0.0)


def test_realized_vol_insufficient_data_returns_none():
    assert realized_vol([100.0]) is None
    assert realized_vol([100.0, 101.0]) is None  # only one return


def test_realized_vol_matches_manual():
    closes = [100.0, 101.0, 102.0, 100.0, 103.0]
    rets = np.diff(np.log(closes))
    expected = rets.std(ddof=1) * np.sqrt(365.0)
    assert realized_vol(closes) == pytest.approx(expected)


def test_atm_iv_at_flat_term_returns_same_iv():
    term = pd.DataFrame({"tte_years": [0.05, 0.25], "atm_iv": [0.6, 0.6]})
    assert atm_iv_at(term, days=30) == pytest.approx(0.6)


def test_atm_iv_at_clamps_beyond_chain():
    term = pd.DataFrame({"tte_years": [0.1, 0.2], "atm_iv": [0.6, 0.5]})
    # 400 days is past the last expiry -> clamps to the far tte, i.e. its ATM IV
    assert atm_iv_at(term, days=400) == pytest.approx(0.5)


def test_atm_iv_at_empty_returns_none():
    assert atm_iv_at(pd.DataFrame({"tte_years": [], "atm_iv": []})) is None
