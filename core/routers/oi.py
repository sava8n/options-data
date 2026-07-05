"""Open-interest routes: open interest by expiration and by strike."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Query

from schemas.oi import (
    OIByExpirationResponse,
    OIByExpirationPoint,
    OIByStrikeResponse,
    OIByStrikePoint,
)
from shared.market_data import load_oi_chain, validate_currency
from oi import by_expiration, by_strike

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oi", tags=["open-interest"])


@router.get("/expiration", response_model=OIByExpirationResponse)
def get_oi_by_expiration(currency: str = Query("BTC")) -> OIByExpirationResponse:
    """BTC open interest by expiration: per-expiry OI split into ITM/OTM calls and puts."""
    cur = validate_currency(currency)
    spot, oi_chain = load_oi_chain(cur)

    grid = by_expiration.build(oi_chain)

    points = [
        OIByExpirationPoint(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            itm_calls=float(row.itm_calls),
            otm_calls=float(row.otm_calls),
            itm_puts=float(row.itm_puts),
            otm_puts=float(row.otm_puts),
        )
        for row in grid.itertuples(index=False)
    ]

    return OIByExpirationResponse(
        currency=cur,
        spot=spot,
        as_of=datetime.now(timezone.utc),
        points=points,
    )


@router.get("/strike", response_model=OIByStrikeResponse)
def get_oi_by_strike(
    currency: str = Query("BTC"),
    expiry: datetime | None = Query(None),
) -> OIByStrikeResponse:
    """BTC open interest by strike: per-strike OI split into ITM/OTM calls and puts.

    Without ``expiry`` the whole chain is grouped by strike. With ``expiry`` the chain
    is sliced to that expiry and the per-strike total intrinsic value (and the max-pain
    strike) are also returned.
    """
    cur = validate_currency(currency)
    spot, oi_chain = load_oi_chain(cur)

    # full expiry list (pre-filter) so the dropdown always has every option.
    expiries = [pd.Timestamp(e).to_pydatetime() for e in sorted(oi_chain["expiry"].unique())]

    chain = oi_chain
    max_pain: float | None = None
    intrinsic_by_strike: dict[float, float] = {}
    if expiry is not None:
        chain = oi_chain[oi_chain["expiry"] == pd.Timestamp(expiry)]
        iv = by_strike.intrinsic_values(chain)
        intrinsic_by_strike = dict(zip(iv["strike"], iv["intrinsic_value"]))
        max_pain = by_strike.max_pain(iv)

    grid = by_strike.build(chain)

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
        spot=spot,
        as_of=datetime.now(timezone.utc),
        expiries=expiries,
        expiry=expiry,
        max_pain=max_pain,
        points=points,
    )
