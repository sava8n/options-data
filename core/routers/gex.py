"""Gamma-exposure route: dollar GEX by strike across the full chain."""

from __future__ import annotations

from fastapi import APIRouter, Query

from schemas.gex import GEXByStrikePoint, GEXByStrikeResponse
from market.loader import load_market_state
from shared.currency import validate_currency

router = APIRouter(prefix="/gex", tags=["gex"])


@router.get("/strike", response_model=GEXByStrikeResponse)
def get_gex_by_strike(currency: str = Query("BTC")) -> GEXByStrikeResponse:
    """Dollar GEX per strike with the zero-gamma flip level."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    points = [
        GEXByStrikePoint(
            strike=float(row.strike),
            call_gex=float(row.call_gex),
            put_gex=float(row.put_gex),
            net_gex=float(row.net_gex),
        )
        for row in state.gex_by_strike.itertuples(index=False)
    ]

    return GEXByStrikeResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        flip=state.gex_flip,
        points=points,
    )
