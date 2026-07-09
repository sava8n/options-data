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


class ProbCurvesResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
    points: list[ProbCurvePoint]
