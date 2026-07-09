"""Option-implied probability curves (P(S_T > K) vs strike, per expiry).

Black-76 under the forward measure: P(S_T > K) = N(d2), one point per
surviving OTM quote using that strike's own mark IV.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from shared.black76 import d2, norm_cdf, valid_mask

logger = logging.getLogger(__name__)

# one row per surviving OTM quote, keyed by strike so each expiry forms a curve
CURVE_COLUMNS = ["expiry", "tte_years", "strike", "prob_above", "option_type"]


def build(prepared_quotes: pd.DataFrame) -> pd.DataFrame:
    """P(S_T > K) = N(d2) per OTM quote, from each strike's own mark IV."""
    logger.info("building implied-probability curves for %d quotes", len(prepared_quotes))

    forward = prepared_quotes["forward"].to_numpy(dtype=float)
    strike = prepared_quotes["strike"].to_numpy(dtype=float)
    tte = prepared_quotes["tte_years"].to_numpy(dtype=float)
    sigma = prepared_quotes["mark_iv"].to_numpy(dtype=float)

    result = prepared_quotes[["expiry", "tte_years", "strike", "option_type"]].copy()
    valid = valid_mask(forward, strike, tte, sigma)
    with np.errstate(divide="ignore", invalid="ignore"):
        result["prob_above"] = np.where(valid, norm_cdf(d2(forward, strike, tte, sigma)), np.nan)
    return result.dropna(subset=["prob_above"])[CURVE_COLUMNS].reset_index(drop=True)
