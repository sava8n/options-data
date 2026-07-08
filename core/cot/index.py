"""Causal rolling min-max COT index: net position within its trailing range, 0-100."""

from __future__ import annotations

import numpy as np
import pandas as pd

from cot.fields import CATEGORIES

WINDOWS = (0, 52, 156, 260)  # weeks; 0 = full history (expanding)
MIN_PERIODS = 52  # an index prints once a year of history exists; larger windows fill partially


def build(history: pd.DataFrame, window: int) -> pd.DataFrame:
    """Per-category index columns aligned to ``history``; NaN before ``MIN_PERIODS``
    or while the range is flat."""
    out = pd.DataFrame(index=history.index)
    for cat in CATEGORIES:
        net = history[f"{cat}_net"]
        if window:
            lo = net.rolling(window, min_periods=MIN_PERIODS).min()
            hi = net.rolling(window, min_periods=MIN_PERIODS).max()
        else:
            lo = net.expanding(min_periods=MIN_PERIODS).min()
            hi = net.expanding(min_periods=MIN_PERIODS).max()
        spread = hi - lo
        out[cat] = np.where(spread > 0, (net - lo) / spread * 100.0, np.nan)
    return out
