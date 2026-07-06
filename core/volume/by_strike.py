"""24h traded volume by strike.

Sums Deribit's per-contract 24h ``volume`` (contracts) per strike, split into
calls and puts. Rides the OI chain, so flow at contracts whose open interest
closed back to zero is not counted.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

VOLUME_BY_STRIKE_COLUMNS = ["strike", "call_volume", "put_volume"]

_SIDES = ["call_volume", "put_volume"]


def _empty_volume_by_strike() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "strike": pd.Series([], dtype="float64"),
            "call_volume": pd.Series([], dtype="float64"),
            "put_volume": pd.Series([], dtype="float64"),
        }
    )


def build(prepared_chain: pd.DataFrame) -> pd.DataFrame:
    """Per-strike 24h volume split into calls and puts; zero-flow strikes dropped."""
    logger.info("building volume by strike")
    if prepared_chain.empty:
        return _empty_volume_by_strike()

    work = prepared_chain[["strike", "volume"]].copy()
    work["side"] = np.where(prepared_chain["option_type"] == "C", "call_volume", "put_volume")

    pivot = work.pivot_table(
        index="strike",
        columns="side",
        values="volume",
        aggfunc="sum",
        fill_value=0.0,
    )
    for col in _SIDES:
        if col not in pivot.columns:
            pivot[col] = 0.0

    result = pivot.reset_index().sort_values("strike").reset_index(drop=True)
    result = result[(result["call_volume"] > 0) | (result["put_volume"] > 0)]
    result = result[VOLUME_BY_STRIKE_COLUMNS].reset_index(drop=True)

    logger.info("volume by strike built for %d strikes", len(result))
    return result
