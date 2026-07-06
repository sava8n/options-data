"""Response models for the traded-volume route."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class VolumeByStrikePoint(BaseModel):
    strike: float
    call_volume: float
    put_volume: float


class VolumeByStrikeResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
    points: list[VolumeByStrikePoint]
