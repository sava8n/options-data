"""Option-greeks route: per-contract delta, gamma, theta and vega across the OTM chain."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query

from schemas.greeks import GreekChainPoint, GreeksChainResponse
from market.loader import load_market_state
from shared.currency import validate_currency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/greeks", tags=["greeks"])


@router.get("/chain", response_model=GreeksChainResponse)
def get_greeks_chain(currency: str = Query("BTC")) -> GreeksChainResponse:
    """All four Black-76 greeks per OTM contract across the chain."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    points = [
        GreekChainPoint(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            strike=float(row.strike),
            option_type=str(row.option_type),
            delta=float(row.delta),
            gamma=float(row.gamma),
            theta=float(row.theta),
            vega=float(row.vega),
        )
        for row in state.greeks_chain.itertuples(index=False)
    ]

    return GreeksChainResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        expiries=state.otm_expiries,
        points=points,
    )
