"""Spot price-history route: daily candles of the ``<currency>_USDC`` pair."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.spot import SpotCandle, SpotHistoryResponse
from market.loader import load_market_state, validate_currency

router = APIRouter(prefix="/spot", tags=["spot"])


@router.get("/history", response_model=SpotHistoryResponse)
def get_spot_history(currency: str = Query("BTC")) -> SpotHistoryResponse:
    """A trailing year of daily spot candles."""
    cur = validate_currency(currency)
    state = load_market_state(cur)
    raw = state.spot_candles

    candles = []
    if raw and raw.get("status") == "ok":
        candles = [
            SpotCandle(
                ts=datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                open=o,
                high=h,
                low=lo,
                close=c,
                volume=v,
            )
            for ts, o, h, lo, c, v in zip(
                raw["ticks"], raw["open"], raw["high"], raw["low"], raw["close"], raw["volume"]
            )
        ]

    return SpotHistoryResponse(
        currency=cur,
        instrument=f"{cur}_USDC",
        as_of=state.as_of,
        candles=candles,
    )
