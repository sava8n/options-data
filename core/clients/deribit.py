"""Deribit public API client."""

from __future__ import annotations

import logging
import time
from typing import Any

import certifi
import requests

logger = logging.getLogger(__name__)

DERIBIT_API = "https://www.deribit.com/api/v2"
HTTP_TIMEOUT = 10


class DeribitError(RuntimeError):
    """Raised when a Deribit request fails or returns an unexpected payload."""


def _get(path: str, params: dict) -> Any:
    start = time.perf_counter()
    try:
        resp = requests.get(
            f"{DERIBIT_API}{path}",
            params=params,
            timeout=HTTP_TIMEOUT,
            verify=certifi.where(),
        )
        resp.raise_for_status()
        result = resp.json()["result"]
    except (requests.RequestException, KeyError, ValueError) as exc:
        logger.warning("Deribit request to %s failed: %s", path, exc)
        raise DeribitError(f"Deribit request to {path} failed: {exc}") from exc
    logger.info("fetched %s in %.0f ms", path, (time.perf_counter() - start) * 1000)
    return result


def fetch_spot(currency: str = "BTC") -> float:
    """Current USD index price for ``currency``, from Deribit's ``<currency>_usd`` index."""
    result = _get("/public/get_index_price", {"index_name": f"{currency.lower()}_usd"})
    return float(result["index_price"])


def fetch_option_summaries(currency: str = "BTC") -> list[dict]:
    """Full option book summary for ``currency``."""
    return _get(
        "/public/get_book_summary_by_currency",
        {"currency": currency.upper(), "kind": "option"},
    )
