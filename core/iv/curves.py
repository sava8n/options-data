"""Implied-volatility smile curves (IV vs strike, per expiry)."""

from __future__ import annotations

import logging
import pandas as pd

logger = logging.getLogger(__name__)

# one row per surviving OTM quote, keyed by strike so each expiry forms a smile.
CURVE_COLUMNS = ["expiry", "tte_years", "strike", "mark_iv", "option_type"]


def build(prepared_quotes: pd.DataFrame) -> pd.DataFrame:
    """BTC IV smile curves: OTM quotes keyed by (strike, expiry)."""
    logger.info("building implied-volatility smile curves")
    return prepared_quotes[CURVE_COLUMNS]
