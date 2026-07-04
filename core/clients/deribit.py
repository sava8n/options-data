"""Shared Deribit public-API client backed by an in-memory TTL cache."""

from __future__ import annotations

import logging
import time
from typing import Any

import certifi
import requests

from config import settings
from shared.cache import TTLCache

logger = logging.getLogger(__name__)

DERIBIT_API = "https://www.deribit.com/api/v2"
HTTP_TIMEOUT = 10

# Deribit spot index names keyed by option currency.
_INDEX_NAMES: dict[str, str] = {"BTC": "btc_usd"}

_cache = TTLCache(settings.cache_ttl_seconds)


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
    """Return the current USD index price for ``currency`` (default BTC)."""
    index_name = _INDEX_NAMES.get(currency.upper())
    if index_name is None:
        raise DeribitError(f"Unsupported currency: {currency}")

    def producer() -> float:
        result = _get("/public/get_index_price", {"index_name": index_name})
        return float(result["index_price"])

    return _cache.get_or_compute(f"spot:{currency.upper()}", producer)


def fetch_option_summaries(currency: str = "BTC") -> list[dict]:
    """Return the full option book summary for ``currency`` (default BTC)."""
    cur = currency.upper()
    if cur not in _INDEX_NAMES:
        raise DeribitError(f"Unsupported currency: {currency}")

    def producer() -> list[dict]:
        return _get(
            "/public/get_book_summary_by_currency",
            {"currency": cur, "kind": "option"},
        )

    return _cache.get_or_compute(f"summaries:{cur}", producer)
