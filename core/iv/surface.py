"""Implied-volatility surface."""

from __future__ import annotations

import logging
import pandas as pd

logger = logging.getLogger(__name__)

GRID_COLUMNS = ["expiry", "tte_years", "delta", "mark_iv", "option_type"]


def build(prepared_quotes: pd.DataFrame) -> pd.DataFrame:
    """BTC IV surface grid: OTM quotes keyed by (delta, expiry)."""
    logger.info("building implied-volatility 3d surface")
    return prepared_quotes[GRID_COLUMNS]
