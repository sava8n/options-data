"""Open interest: ITM/OTM bucketing by expiration and strike, intrinsic value and max pain."""

from __future__ import annotations

import pandas as pd
import pytest

from oi.by_expiration import OI_BY_EXPIRATION_COLUMNS, build as build_by_expiration
from oi.by_strike import (
    OI_BY_STRIKE_COLUMNS,
    build as build_by_strike,
    intrinsic_values,
    max_pain,
)

_EXPIRY = pd.Timestamp("2035-01-31", tz="UTC")
_CHAIN_COLUMNS = ["expiry", "tte_years", "strike", "forward", "option_type", "open_interest"]


def _chain(rows):
    return pd.DataFrame(rows, columns=_CHAIN_COLUMNS)


def test_by_expiration_bucketing():
    # forward 100: call K=90 is ITM, call K=110 is OTM; put K=110 is ITM, put K=90 is OTM
    chain = _chain(
        [
            (_EXPIRY, 0.1, 90.0, 100.0, "C", 10.0),
            (_EXPIRY, 0.1, 110.0, 100.0, "C", 20.0),
            (_EXPIRY, 0.1, 110.0, 100.0, "P", 5.0),
            (_EXPIRY, 0.1, 90.0, 100.0, "P", 7.0),
        ]
    )
    out = build_by_expiration(chain)
    assert list(out.columns) == OI_BY_EXPIRATION_COLUMNS
    row = out.iloc[0]
    assert row["itm_calls"] == 10.0
    assert row["otm_calls"] == 20.0
    assert row["itm_puts"] == 5.0
    assert row["otm_puts"] == 7.0


def test_by_expiration_empty_is_typed():
    out = build_by_expiration(_chain([]))
    assert out.empty
    assert list(out.columns) == OI_BY_EXPIRATION_COLUMNS


def test_by_strike_bucketing():
    chain = _chain(
        [
            (_EXPIRY, 0.1, 90.0, 100.0, "C", 10.0),  # call, K < F -> ITM
            (_EXPIRY, 0.1, 90.0, 100.0, "P", 7.0),   # put,  K < F -> OTM
        ]
    )
    out = build_by_strike(chain)
    assert list(out.columns) == OI_BY_STRIKE_COLUMNS
    row = out[out["strike"] == 90.0].iloc[0]
    assert row["itm_calls"] == 10.0
    assert row["otm_puts"] == 7.0


def test_intrinsic_value_and_max_pain():
    # one call at 100 and one put at 120 (each 1 contract); candidates are {100, 120}
    chain = _chain(
        [
            (_EXPIRY, 0.1, 100.0, 110.0, "C", 1.0),
            (_EXPIRY, 0.1, 120.0, 110.0, "P", 1.0),
        ]
    )
    intrinsic = intrinsic_values(chain)
    by_strike = dict(zip(intrinsic["strike"], intrinsic["intrinsic_value"]))
    # settle at 100: call pays 0, put pays (120-100)=20 -> 20
    assert by_strike[100.0] == pytest.approx(20.0)
    # settle at 120: call pays (120-100)=20, put pays 0 -> 20
    assert by_strike[120.0] == pytest.approx(20.0)
    # tie -> the lowest-indexed (smallest) strike wins
    assert max_pain(intrinsic) == pytest.approx(100.0)


def test_max_pain_empty_returns_none():
    empty = pd.DataFrame({"strike": [], "option_type": [], "open_interest": []})
    assert max_pain(intrinsic_values(empty)) is None
