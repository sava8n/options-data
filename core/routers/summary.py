"""Dashboard summary route: spot, as-of and chain size."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from schemas.summary import SummaryResponse
from shared.market_data import load_otm_quotes, validate_currency

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(currency: str = Query("BTC")) -> SummaryResponse:
    """Lightweight market summary derived from the shared prepared-quote cache."""
    cur = validate_currency(currency)
    spot, otm_quotes = load_otm_quotes(cur)
    return SummaryResponse(
        currency=cur,
        spot=spot,
        as_of=datetime.now(timezone.utc),
        instrument_count=len(otm_quotes),
        expiry_count=int(otm_quotes["expiry"].nunique()),
    )
