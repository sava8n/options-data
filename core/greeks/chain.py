"""Build a per-contract greek table across the OTM option chain."""

from __future__ import annotations

import logging

import pandas as pd

from greeks import delta, gamma, theta, vega

logger = logging.getLogger(__name__)

# greek name -> module exposing compute(forward, strike, tte, sigma, is_call)
GREEKS = {module.NAME: module for module in (delta, gamma, theta, vega)}

# one row per OTM quote; `value` holds the selected greek, keyed by (strike, expiry)
GREEK_COLUMNS = ["expiry", "tte_years", "strike", "value", "option_type"]


def build_greek(prepared_quotes: pd.DataFrame, greek: str) -> pd.DataFrame:
    """OTM per-contract values of ``greek`` keyed by (strike, expiry)."""
    if greek not in GREEKS:
        raise ValueError(f"unknown greek '{greek}'; expected one of {sorted(GREEKS)}")

    logger.info("building %s greek", greek)
    result = prepared_quotes[["expiry", "tte_years", "strike", "option_type"]].copy()
    result["value"] = GREEKS[greek].compute(
        prepared_quotes["forward"].to_numpy(dtype=float),
        prepared_quotes["strike"].to_numpy(dtype=float),
        prepared_quotes["tte_years"].to_numpy(dtype=float),
        prepared_quotes["mark_iv"].to_numpy(dtype=float),
        (prepared_quotes["option_type"] == "C").to_numpy(),
    )
    return result[GREEK_COLUMNS]
