"""Spot price route."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.spot import SpotResponse
from shared.market_data import load_spot, validate_currency

router = APIRouter(tags=["spot"])


@router.get("/spot", response_model=SpotResponse)
def get_spot(currency: str = Query("BTC")) -> SpotResponse:
    """Current spot index price."""
    cur = validate_currency(currency)
    return SpotResponse(
        currency=cur,
        spot=load_spot(cur),
        as_of=datetime.now(timezone.utc),
    )
