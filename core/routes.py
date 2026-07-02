"""API routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from config import settings
from schemas import HealthResponse, IVSurfaceResponse, SurfacePoint
from clients import deribit
from clients.deribit import DeribitError
from volatility import iv_surface

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/iv-surface", response_model=IVSurfaceResponse)
def get_iv_surface(currency: str = Query("BTC")) -> IVSurfaceResponse:
    """BTC options implied-volatility surface: (delta, expiry) -> IV, plus axis ticks."""
    cur = currency.upper()
    if cur not in settings.supported_currency_list:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported currency '{currency}'. Supported: {settings.supported_currency_list}",
        )

    try:
        spot = deribit.fetch_spot(cur)
        summaries = deribit.fetch_option_summaries(cur)
    except DeribitError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    grid = iv_surface.build_surface(summaries, spot)

    points = [
        SurfacePoint(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            delta=float(row.delta),
            mark_iv=float(row.mark_iv),
            option_type=str(row.option_type),
        )
        for row in grid.itertuples(index=False)
    ]

    return IVSurfaceResponse(
        currency=cur,
        spot=spot,
        as_of=datetime.now(timezone.utc),
        points=points,
    )
