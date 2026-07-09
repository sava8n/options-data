"""Traded-volume route: 24h volume by strike across the full chain."""

from __future__ import annotations

from fastapi import APIRouter, Query

from schemas.volume import VolumeByStrikePoint, VolumeByStrikeResponse
from market.loader import load_market_state, validate_currency

router = APIRouter(prefix="/volume", tags=["volume"])


@router.get("/strike", response_model=VolumeByStrikeResponse)
def get_volume_by_strike(currency: str = Query("BTC")) -> VolumeByStrikeResponse:
    """24h traded volume per strike, split into calls and puts."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    points = [
        VolumeByStrikePoint(
            strike=float(row.strike),
            call_volume=float(row.call_volume),
            put_volume=float(row.put_volume),
        )
        for row in state.volume_by_strike.itertuples(index=False)
    ]

    return VolumeByStrikeResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        points=points,
    )
