"""Response model for the spot price route."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SpotResponse(BaseModel):
    currency: str
    spot: float
    as_of: datetime
