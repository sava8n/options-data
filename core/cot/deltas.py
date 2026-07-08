"""Net positions (long minus short, spread excluded) and report-over-report diffs."""

from __future__ import annotations

import pandas as pd

from cot.fields import CATEGORIES


def build(agg: pd.DataFrame) -> pd.DataFrame:
    out = agg.copy()
    for cat in CATEGORIES:
        out[f"{cat}_net"] = out[f"{cat}_long"] - out[f"{cat}_short"]
        out[f"{cat}_delta"] = out[f"{cat}_net"].diff()
    out["oi_delta"] = out["oi"].diff()
    return out
