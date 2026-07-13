"""Option-implied probability routes."""

from __future__ import annotations

import logging

import pandas as pd
from fastapi import APIRouter, Query

from schemas.prob import ProbCurvePoint, ProbCurvesResponse, ProbQuantileRow
from market.loader import load_market_state
from shared.currency import validate_currency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prob", tags=["probabilities"])


@router.get("/curves", response_model=ProbCurvesResponse)
def get_prob_curves(currency: str = Query("BTC")) -> ProbCurvesResponse:
    """Option-implied P(S_T > K): (strike, expiry) -> probability, one curve per expiry."""
    cur = validate_currency(currency)
    state = load_market_state(cur)

    points = [
        ProbCurvePoint(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            strike=float(row.strike),
            prob_above=float(row.prob_above),
            option_type=str(row.option_type),
        )
        for row in state.prob_curves.itertuples(index=False)
    ]

    quantiles = [
        ProbQuantileRow(
            expiry=row.expiry.to_pydatetime(),
            tte_years=float(row.tte_years),
            p16=float(row.p16) if pd.notna(row.p16) else None,
            p50=float(row.p50) if pd.notna(row.p50) else None,
            p84=float(row.p84) if pd.notna(row.p84) else None,
        )
        for row in state.prob_quantiles.itertuples(index=False)
    ]

    return ProbCurvesResponse(
        currency=cur,
        spot=state.spot,
        as_of=state.as_of,
        points=points,
        quantiles=quantiles,
    )