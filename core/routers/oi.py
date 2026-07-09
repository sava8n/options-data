"""Open-interest routes: open interest by expiration and by strike."""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Query

from schemas.oi import (
    OIByExpirationResponse,
    OIByExpirationPoint,
    OIByStrikeResponse,
    OIByStrikePoint,
)
from market.loader import load_market_state
from shared.currency import validate_currency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oi", tags=["open-interest"])


@router.get("/expiration", response_model=OIByExpirationResponse)
def get_oi_by_expiration(currency: str = Query("BTC")) -> OIByExpirationResponse:
    """Open interest by expiration: per-expiry OI split into ITM/OTM calls and puts."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    points = [
        OIByExpirationPoint(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            itm_calls=float(row.itm_calls),
            otm_calls=float(row.otm_calls),
            itm_puts=float(row.itm_puts),
            otm_puts=float(row.otm_puts),
        )
        for row in state.oi_by_expiration.itertuples(index=False)
    ]

    return OIByExpirationResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        points=points,
    )


@router.get("/strike", response_model=OIByStrikeResponse)
def get_oi_by_strike(
    currency: str = Query("BTC"),
    expiry: datetime | None = Query(None),
) -> OIByStrikeResponse:
    """Open interest by strike: per-strike OI split into ITM/OTM calls and puts.

    Without ``expiry`` the whole chain is grouped by strike. With ``expiry`` the chain
    is sliced to that expiry and the per-strike total intrinsic value (and the max-pain
    strike) are also returned.
    """
    cur = validate_currency(currency)
    state = load_market_state(cur)

    grid, intrinsic_by_strike, max_pain = state.oi_by_strike(
        pd.Timestamp(expiry) if expiry is not None else None
    )

    points = [
        OIByStrikePoint(
            strike=float(row.strike),
            itm_calls=float(row.itm_calls),
            otm_calls=float(row.otm_calls),
            itm_puts=float(row.itm_puts),
            otm_puts=float(row.otm_puts),
            intrinsic_value=(
                float(intrinsic_by_strike[row.strike]) if expiry is not None else None
            ),
        )
        for row in grid.itertuples(index=False)
    ]

    return OIByStrikeResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        expiries=state.oi_expiries,
        expiry=expiry,
        max_pain=max_pain,
        points=points,
    )
