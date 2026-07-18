"""Implied-probability pipeline: smile smoothing, survival curves and strike quantiles."""

from __future__ import annotations

import numpy as np
import pytest

from prob.curves import CURVE_COLUMNS, build as build_curves
from prob.quantiles import QUANTILE_COLUMNS, build as build_quantiles, invert_survival
from prob.smile import smooth_smile


def test_smooth_smile_recovers_linear_slope():
    k = np.linspace(-0.2, 0.2, 9)
    sigma = 0.6 + 0.5 * k  # exactly linear -> local quadratic fit is exact
    smoothed, slope = smooth_smile(k, sigma)
    np.testing.assert_allclose(smoothed, sigma, atol=1e-6)
    np.testing.assert_allclose(slope, 0.5, atol=1e-6)


def test_smooth_smile_flat_has_zero_slope():
    k = np.linspace(-0.2, 0.2, 9)
    sigma = np.full_like(k, 0.6)
    smoothed, slope = smooth_smile(k, sigma)
    np.testing.assert_allclose(smoothed, 0.6, atol=1e-9)
    np.testing.assert_allclose(slope, 0.0, atol=1e-9)


def test_build_curves_bounds_and_monotone(otm_quotes):
    curves = build_curves(otm_quotes)
    assert set(CURVE_COLUMNS).issubset(curves.columns)
    prob = curves["prob_above"].to_numpy()
    assert ((prob >= 0.0) & (prob <= 1.0)).all()
    # a survival curve is non-increasing in strike within each expiry
    for _, group in curves.groupby("expiry"):
        ordered = group.sort_values("strike")["prob_above"].to_numpy()
        assert np.all(np.diff(ordered) <= 1e-9)


def test_invert_survival_interpolates_median():
    strike = np.array([90.0, 100.0, 110.0])
    prob = np.array([0.9, 0.5, 0.1])  # non-increasing survival
    assert invert_survival(strike, prob, 0.50) == pytest.approx(100.0)


def test_invert_survival_out_of_range_is_nan():
    strike = np.array([90.0, 100.0, 110.0])
    prob = np.array([0.9, 0.5, 0.1])
    # target = 1 - 0.02 = 0.98 sits above the top of the curve (0.9) -> no extrapolation
    assert np.isnan(invert_survival(strike, prob, 0.02))


def test_invert_survival_needs_two_points():
    assert np.isnan(invert_survival(np.array([100.0]), np.array([0.5]), 0.5))


def test_build_quantiles_ordering(otm_quotes):
    quantiles = build_quantiles(build_curves(otm_quotes))
    assert list(quantiles.columns) == QUANTILE_COLUMNS
    row = quantiles.dropna().iloc[0]
    assert row["p16"] <= row["p50"] <= row["p84"]
