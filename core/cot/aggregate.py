"""Weight per-contract rows by contract size and sum into one BTC-equivalent row per report date."""

from __future__ import annotations

import pandas as pd

from cot.fields import CATEGORIES, CONTRACT_WEIGHTS

POSITION_COLS = ["oi"] + [f"{cat}_{side}" for cat in CATEGORIES for side in ("long", "short", "spread")]
TRADER_COLS = [f"traders_{cat}_{side}" for cat in CATEGORIES for side in ("long", "short")]


def build(tidy: pd.DataFrame) -> pd.DataFrame:
    """Frame indexed by report_date; positions in BTC-equivalent, trader counts summed."""
    weights = tidy["code"].map(CONTRACT_WEIGHTS).fillna(0.0)
    weighted = tidy[POSITION_COLS].mul(weights, axis=0)
    grouped = pd.concat([tidy[["report_date"]], weighted, tidy[TRADER_COLS]], axis=1).groupby(
        "report_date", sort=True
    )
    # min_count keeps structurally-absent trader counts (nonrept) as NaN instead of 0
    return grouped[POSITION_COLS].sum().join(grouped[TRADER_COLS].sum(min_count=1))
