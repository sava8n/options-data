"""Black-76 greeks: closed-form deltas/gammas/thetas/vegas and the chain builder."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from greeks import delta, gamma, theta, vega
from greeks.chain import CHAIN_COLUMNS, build_chain
from shared.black76 import norm_pdf

_GREEK_COLS = ["delta", "gamma", "theta", "vega"]


def test_delta_from_d1_call_vs_put():
    d1 = np.array([0.0, 0.5])
    call = delta.from_d1(d1, np.array([True, True]))
    put = delta.from_d1(d1, np.array([False, False]))
    np.testing.assert_allclose(call - put, 1.0)
    assert call[0] == pytest.approx(0.5)  # N(0) = 0.5


def test_gamma_positive_and_formula():
    pdf = norm_pdf(np.array([0.0]))
    g = gamma.from_d1(pdf, np.array([100.0]), np.array([0.6]), np.array([0.5]))
    assert g[0] > 0
    np.testing.assert_allclose(g, pdf / (100.0 * 0.6 * 0.5))


def test_theta_non_positive_and_day_scaling():
    pdf = norm_pdf(np.array([0.0]))
    th = theta.from_d1(pdf, np.array([100.0]), np.array([0.6]), np.array([0.5]))
    assert th[0] < 0
    expected = -100.0 * pdf * 0.6 / (2.0 * 0.5) / theta.DAYS_PER_YEAR
    np.testing.assert_allclose(th, expected)


def test_vega_positive_and_vol_point_scaling():
    pdf = norm_pdf(np.array([0.0]))
    v = vega.from_d1(pdf, np.array([100.0]), np.array([0.5]))
    assert v[0] > 0
    np.testing.assert_allclose(v, 100.0 * pdf * 0.5 * vega.VOL_POINT)


def test_build_chain_columns_and_all_valid(otm_quotes):
    chain = build_chain(otm_quotes)
    assert list(chain.columns) == CHAIN_COLUMNS
    assert len(chain) == len(otm_quotes)
    assert chain[_GREEK_COLS].notna().all().all()
    # gamma and vega are non-negative; theta is non-positive
    assert (chain["gamma"] >= 0).all()
    assert (chain["vega"] >= 0).all()
    assert (chain["theta"] <= 0).all()


def test_build_chain_nan_for_invalid_row():
    # a zero-tte contract fails valid_mask, so every greek must be NaN
    quotes = pd.DataFrame(
        {
            "expiry": pd.to_datetime(["2035-01-31"], utc=True),
            "tte_years": [0.0],
            "strike": [100.0],
            "option_type": ["C"],
            "forward": [100.0],
            "mark_iv": [0.6],
        }
    )
    chain = build_chain(quotes)
    assert chain[_GREEK_COLS].isna().all().all()
