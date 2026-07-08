"""Raw Socrata records to a tidy per-(report_date, contract) frame with canonical columns."""

from __future__ import annotations

import logging

import pandas as pd

from cot.fields import CATEGORIES, CODE_FIELD, DATE_FIELD, OI_FIELD, POSITION_FIELDS, TRADER_FIELDS

logger = logging.getLogger(__name__)


def _numeric(frame: pd.DataFrame, field: str | None, fill: float | None) -> pd.Series:
    if field is None:
        return pd.Series(float("nan"), index=frame.index, dtype="float64")
    if field not in frame.columns:
        # a wholesale-missing column means the Socrata schema changed under us
        logger.warning("CFTC field missing from payload: %s", field)
        return pd.Series(fill, index=frame.index, dtype="float64")
    values = pd.to_numeric(frame[field], errors="coerce")
    return values.fillna(fill) if fill is not None else values


def build(records: list[dict]) -> pd.DataFrame:
    if not records:
        raise ValueError("CFTC returned no records")
    frame = pd.DataFrame(records)
    for field in (DATE_FIELD, CODE_FIELD):
        if field not in frame.columns:
            raise ValueError(f"CFTC payload missing field: {field}")
    tidy = pd.DataFrame(
        {
            "report_date": pd.to_datetime(frame[DATE_FIELD]),
            "code": frame[CODE_FIELD].astype(str),
            "oi": _numeric(frame, OI_FIELD, 0.0),
        }
    )
    for cat in CATEGORIES:
        for side in ("long", "short", "spread"):
            tidy[f"{cat}_{side}"] = _numeric(frame, POSITION_FIELDS[cat][side], 0.0)
        for side in ("long", "short"):
            # absent keys mean zero traders; structurally missing series stay NaN
            tidy[f"traders_{cat}_{side}"] = _numeric(frame, TRADER_FIELDS[cat][side], 0.0)
    return (
        tidy.sort_values(["report_date", "code"])
        .drop_duplicates(subset=["report_date", "code"], keep="last")
        .reset_index(drop=True)
    )
