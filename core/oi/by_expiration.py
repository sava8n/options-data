"""Open interest by expiration (ITM/OTM calls and puts summed per expiry)."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# one row per expiry: open interest (contracts) split into
# four moneyness buckets, sorted by time to expiry.
OI_BY_EXPIRATION_COLUMNS = ["expiry", "tte_years", "itm_calls", "otm_calls", "itm_puts", "otm_puts"]

_BUCKETS = ["itm_calls", "otm_calls", "itm_puts", "otm_puts"]


def _empty_oi_by_expiration() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "expiry": pd.Series([], dtype="datetime64[ns, UTC]"),
            "tte_years": pd.Series([], dtype="float64"),
            "itm_calls": pd.Series([], dtype="float64"),
            "otm_calls": pd.Series([], dtype="float64"),
            "itm_puts": pd.Series([], dtype="float64"),
            "otm_puts": pd.Series([], dtype="float64"),
        }
    )


def build(prepared_chain: pd.DataFrame) -> pd.DataFrame:
    """Open interest by expiration: per-expiry OI split into ITM/OTM calls and puts.

    ITM/OTM is classified by strike vs the per-contract forward (no IV needed):
    a call is ITM when ``strike < forward``, a put when ``strike > forward``
    (at-the-money strikes fall to OTM). Open interest is Deribit's per-contract
    count and is summed within each (expiry, bucket). Rows are sorted by tte.
    """
    logger.info("building OI by expiration")
    if prepared_chain.empty:
        return _empty_oi_by_expiration()

    is_call = (prepared_chain["option_type"] == "C").to_numpy()
    strike = prepared_chain["strike"].to_numpy(dtype=float)
    forward = prepared_chain["forward"].to_numpy(dtype=float)
    itm = np.where(is_call, strike < forward, strike > forward)

    bucket = np.select(
        [is_call & itm, is_call & ~itm, ~is_call & itm, ~is_call & ~itm],
        _BUCKETS,
        default="",
    )

    work = prepared_chain[["expiry", "tte_years", "open_interest"]].copy()
    work["bucket"] = bucket

    # sum OI per (expiry, bucket), then spread the buckets into columns.
    pivot = work.pivot_table(
        index="expiry",
        columns="bucket",
        values="open_interest",
        aggfunc="sum",
        fill_value=0.0,
    )
    for col in _BUCKETS:
        if col not in pivot.columns:
            pivot[col] = 0.0

    tte = work.groupby("expiry")["tte_years"].first()
    result = (
        pivot.join(tte)
        .reset_index()
        .sort_values("tte_years")
        .reset_index(drop=True)
    )
    result["expiry"] = pd.to_datetime(result["expiry"], utc=True)
    result = result[OI_BY_EXPIRATION_COLUMNS]

    logger.info("OI by expiration built for %d expiries", len(result))
    return result
