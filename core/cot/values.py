"""NaN-to-None coercion for optional response fields."""

from __future__ import annotations

import pandas as pd


def opt_float(value) -> float | None:
    return None if value is None or pd.isna(value) else float(value)


def opt_int(value) -> int | None:
    return None if value is None or pd.isna(value) else int(value)
