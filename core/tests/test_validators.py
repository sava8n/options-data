"""Request validators: currency, COT window and COT method all reject with HTTP 422."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from routers.cot import _validate_method, _validate_window
from shared.currency import validate_currency


def test_validate_currency_normalizes_case():
    assert validate_currency("btc") == "BTC"


def test_validate_currency_rejects_unsupported():
    with pytest.raises(HTTPException) as exc:
        validate_currency("xyz")
    assert exc.value.status_code == 422


def test_validate_window():
    assert _validate_window(52) == 52
    with pytest.raises(HTTPException) as exc:
        _validate_window(999)
    assert exc.value.status_code == 422


def test_validate_method():
    assert _validate_method("rank") == "rank"
    with pytest.raises(HTTPException) as exc:
        _validate_method("bogus")
    assert exc.value.status_code == 422
