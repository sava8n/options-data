"""One consistent view of the COT feed: tidy input plus the derived data graph.

Derived products compute on first access and are memoized for the object's
lifetime - one cache TTL window, so every endpoint serves the same numbers.
"""

from __future__ import annotations

from datetime import datetime
from functools import cached_property

import pandas as pd

from cot import aggregate, deltas
from cot import index as index_mod
from cot import prices as prices_mod
from cot.contracts import CotSpec


class CotState:
    def __init__(
        self, as_of: datetime, spec: CotSpec, tidy: pd.DataFrame, price_candles: dict | None
    ) -> None:
        self.as_of = as_of
        self.spec = spec
        self.tidy = tidy  # shared across requests; treat as read-only
        self.price_candles = price_candles  # TradingView arrays since the report era or None
        self._index_cache: dict[tuple[int, str], pd.DataFrame] = {}

    @property
    def currency(self) -> str:
        return self.spec.currency

    @cached_property
    def history(self) -> pd.DataFrame:
        """Coin-equivalent aggregate with nets and deltas, indexed by report_date."""
        return deltas.build(aggregate.build(self.tidy, self.spec.weights))

    def index(self, window: int, method: str) -> pd.DataFrame:
        key = (window, method)
        frame = self._index_cache.get(key)
        if frame is None:
            frame = index_mod.build(self.history, window, method)
            self._index_cache[key] = frame
        return frame

    @cached_property
    def weekly_prices(self) -> pd.Series:
        return prices_mod.align(self.price_candles, self.history.index)

    @cached_property
    def micro_included_from(self) -> pd.Timestamp | None:
        micro = self.tidy.loc[self.tidy["code"] == self.spec.micro_code, "report_date"]
        return None if micro.empty else micro.min()

    @cached_property
    def price_from(self) -> pd.Timestamp | None:
        valid = self.weekly_prices.dropna()
        return None if valid.empty else valid.index.min()
