"""Market stats route: spot, DVOL (+rank) and 30-day implied vs realized vol."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.stats import StatsResponse
from market.loader import load_market_state, validate_currency

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def get_stats(currency: str = Query("BTC")) -> StatsResponse:
    """Stats: spot, DVOL with its trailing-year rank, 30d ATM IV vs realized vol."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    return StatsResponse(
        currency=cur,
        spot=state.spot,
        as_of=datetime.now(timezone.utc),
        dvol=state.dvol,
        dvol_rank=state.dvol_rank,
        iv30=state.iv30,
        rv30=state.rv30,
    )
