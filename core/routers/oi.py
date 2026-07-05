"""Open-interest routes: open interest by expiration."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.oi import OIByExpirationResponse, OIByExpirationPoint
from shared.market_data import load_oi_chain, validate_currency
from oi import by_expiration

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
