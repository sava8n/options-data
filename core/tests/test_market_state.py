"""MarketState wires the pure builders together off in-memory frames (no network)."""

from __future__ import annotations

import pandas as pd


def test_derived_products_build(market_state):
    greeks = market_state.greeks_chain
    assert not greeks.empty
    assert greeks[["delta", "gamma", "theta", "vega"]].notna().all().all()

    curves = market_state.prob_curves
    assert not curves.empty
    assert ((curves["prob_above"] >= 0.0) & (curves["prob_above"] <= 1.0)).all()

    assert not market_state.oi_by_expiration.empty
    assert not market_state.volume_by_strike.empty
    assert not market_state.gex_by_strike.empty


def test_scalar_stats(market_state):
    assert market_state.iv30 is not None and market_state.iv30 > 0
    assert market_state.dvol is not None
    assert market_state.dvol_rank is not None
    assert market_state.rv30 is not None


def test_oi_by_strike_single_expiry_slice(market_state):
    expiry = market_state.oi_expiries[0]
    grid, intrinsic, max_pain = market_state.oi_by_strike(pd.Timestamp(expiry))
    assert not grid.empty
    assert intrinsic  # non-empty dict of strike -> intrinsic value
    assert max_pain is not None
