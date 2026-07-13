"""Response models for option-implied probability routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProbCurvePoint(BaseModel):
    expiry: datetime
    tte_years: float
    strike: float
    prob_above: float  # P(S_T > K) under the forward measure, in [0, 1]
    option_type: str


class ProbQuantileRow(BaseModel):
    expiry: datetime
    tte_years: float
    p16: float | None  # K with P(S_T <= K) = 0.16; None when the curve does not span it
    p50: float | None
    p84: float | None


class ProbCurvesResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
    points: list[ProbCurvePoint]
    quantiles: list[ProbQuantileRow]
