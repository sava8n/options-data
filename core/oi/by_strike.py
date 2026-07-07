"""Open interest by strike (ITM/OTM calls and puts summed per strike, plus max pain)."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# one row per strike: open interest (contracts) split into 
# four moneyness buckets, sorted by strike
OI_BY_STRIKE_COLUMNS = ["strike", "itm_calls", "otm_calls", "itm_puts", "otm_puts"]

_BUCKETS = ["itm_calls", "otm_calls", "itm_puts", "otm_puts"]


def _empty_oi_by_strike() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "strike": pd.Series([], dtype="float64"),
            "itm_calls": pd.Series([], dtype="float64"),
            "otm_calls": pd.Series([], dtype="float64"),
            "itm_puts": pd.Series([], dtype="float64"),
            "otm_puts": pd.Series([], dtype="float64"),
        }
    )


def build(prepared_chain: pd.DataFrame) -> pd.DataFrame:
    """Open interest by strike: per-strike OI split into ITM/OTM calls and puts.

    ITM/OTM is classified by strike vs the per-contract forward (no IV needed):
    a call is ITM when ``strike < forward``, a put when ``strike > forward``
    (at-the-money strikes fall to OTM). Open interest is Deribit's per-contract
    count and is summed within each (strike, bucket). Rows are sorted by strike.
    The chain may be the full chain or a single-expiry slice.
    """
    logger.info("building open interest by strike")
    if prepared_chain.empty:
        return _empty_oi_by_strike()

    is_call = (prepared_chain["option_type"] == "C").to_numpy()
    strike = prepared_chain["strike"].to_numpy(dtype=float)
    forward = prepared_chain["forward"].to_numpy(dtype=float)
    itm = np.where(is_call, strike < forward, strike > forward)

    bucket = np.select(
        [is_call & itm, is_call & ~itm, ~is_call & itm, ~is_call & ~itm],
        _BUCKETS,
        default="",
    )

    work = prepared_chain[["strike", "open_interest"]].copy()
    work["bucket"] = bucket

    # sum OI per (strike, bucket), then spread the buckets into columns
    pivot = work.pivot_table(
        index="strike",
        columns="bucket",
        values="open_interest",
        aggfunc="sum",
        fill_value=0.0,
    )
    for col in _BUCKETS:
        if col not in pivot.columns:
            pivot[col] = 0.0

    result = pivot.reset_index().sort_values("strike").reset_index(drop=True)
    result = result[OI_BY_STRIKE_COLUMNS]

    logger.info("open interest by strike built for %d strikes", len(result))
    return result


def intrinsic_values(prepared_chain: pd.DataFrame) -> pd.DataFrame:
    """Total open-interest-weighted intrinsic value at each candidate settlement price.

    The candidate settlement prices are the distinct strikes present in the chain.
    For a candidate price ``K`` the total intrinsic (cash) value across the chain is
    ``sum(call_oi * max(K - Ki, 0)) + sum(put_oi * max(Ki - K, 0))`` in USD -- what
    all outstanding options would pay out if the underlying settled at ``K``. The
    max-pain strike is the candidate that minimises this. Intended for a single
    expiry (mixing expiries conflates unrelated settlement dates).

    Returns one row per candidate strike: ``[strike, intrinsic_value]``.
    """
    if prepared_chain.empty:
        return pd.DataFrame(
            {"strike": pd.Series([], dtype="float64"), "intrinsic_value": pd.Series([], dtype="float64")}
        )

    is_call = (prepared_chain["option_type"] == "C").to_numpy()
    strike = prepared_chain["strike"].to_numpy(dtype=float)
    oi = prepared_chain["open_interest"].to_numpy(dtype=float)

    candidates = np.unique(strike)
    # broadcast candidates (rows) against contracts (cols): payoff of each contract
    # if the underlying settled at each candidate price
    diff = candidates[:, None] - strike[None, :]
    call_payoff = np.where(is_call[None, :], np.maximum(diff, 0.0), 0.0)
    put_payoff = np.where(~is_call[None, :], np.maximum(-diff, 0.0), 0.0)
    total = ((call_payoff + put_payoff) * oi[None, :]).sum(axis=1)

    return pd.DataFrame({"strike": candidates, "intrinsic_value": total})


def max_pain(intrinsic: pd.DataFrame) -> float | None:
    """The strike with the least total intrinsic value (max-pain price), or None."""
    if intrinsic.empty:
        return None
    row = intrinsic.loc[intrinsic["intrinsic_value"].idxmin()]
    return float(row["strike"])
