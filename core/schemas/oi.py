"""Response models for open-interest routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OIByExpirationPoint(BaseModel):
    expiry: datetime
    tte_years: float
    itm_calls: float
    otm_calls: float
    itm_puts: float
    otm_puts: float


class OIByExpirationResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
    points: list[OIByExpirationPoint]


class OIByStrikePoint(BaseModel):
    strike: float
    itm_calls: float
    otm_calls: float
    itm_puts: float
    otm_puts: float
    intrinsic_value: float | None = None  # populated only for a single expiry


class OIByStrikeResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
    expiries: list[datetime]
    expiry: datetime | None = None  # echo of the selected expiry; None = all
    max_pain: float | None = None  # populated only for a single expiry
    points: list[OIByStrikePoint]
