"""Traded-volume route: 24h volume by strike across the full chain."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.volume import VolumeByStrikePoint, VolumeByStrikeResponse
from shared.market_data import load_oi_chain, validate_currency
from volume import by_strike

router = APIRouter(prefix="/volume", tags=["volume"])


@router.get("/strike", response_model=VolumeByStrikeResponse)
def get_volume_by_strike(currency: str = Query("BTC")) -> VolumeByStrikeResponse:
    """24h traded volume per strike, split into calls and puts."""
    cur = validate_currency(currency)
    spot, oi_chain = load_oi_chain(cur)

    grid = by_strike.build(oi_chain)

    points = [
        VolumeByStrikePoint(
            strike=float(row.strike),
            call_volume=float(row.call_volume),
            put_volume=float(row.put_volume),
        )
        for row in grid.itertuples(index=False)
    ]

    return VolumeByStrikeResponse(
        currency=cur,
        spot=spot,
        as_of=datetime.now(timezone.utc),
        points=points,
    )
