"""Response models for COT routes. Position values are coin-equivalent contracts.

Every response names its ``currency``, so the position fields carry no unit suffix.
Report dates are plain dates: a naive-datetime serialization would be parsed as
local time by the browser and can render one day off.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class CotReportRow(BaseModel):
    category: str
    label: str
    long: float
    short: float
    spread: float | None = None  # None, category has no spread series
    net: float
    delta_net: float | None = None  # None on the first report
    delta_net_pct: float | None = None  # None when the prior net sits at zero
    net_pct_of_oi: float | None = None
    index: float | None = None  # None while the window is unfilled
    traders_long: int | None = None  # None, CFTC reports no nonrept counts
    traders_short: int | None = None


class CotReportResponse(BaseModel):
    currency: str
    as_of: datetime
    report_date: date
    prev_report_date: date | None
    publication_date: date
    is_new: bool
    is_stale: bool
    window: int
    method: str
    oi: float
    delta_oi: float | None
    price: float | None
    oi_usd: float | None
    micro_included_from: date | None
    rows: list[CotReportRow]


class CotHistoryPoint(BaseModel):
    report_date: date
    oi: float
    price: float | None = None
    dealer_net: float
    dealer_delta: float | None = None
    asset_mgr_net: float
    asset_mgr_delta: float | None = None
    lev_money_net: float
    lev_money_delta: float | None = None
    other_rept_net: float
    other_rept_delta: float | None = None
    nonrept_net: float
    nonrept_delta: float | None = None


class CotHistoryResponse(BaseModel):
    currency: str
    as_of: datetime
    micro_included_from: date | None
    price_from: date | None
    points: list[CotHistoryPoint]


class CotIndexPoint(BaseModel):
    report_date: date
    dealer: float | None = None
    asset_mgr: float | None = None
    lev_money: float | None = None
    other_rept: float | None = None
    nonrept: float | None = None


class CotIndexResponse(BaseModel):
    currency: str
    as_of: datetime
    window: int
    method: str
    points: list[CotIndexPoint]
