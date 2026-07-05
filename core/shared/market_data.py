"""Shared request helpers."""

from __future__ import annotations

import logging

import pandas as pd
from fastapi import HTTPException

from config import settings
from clients import deribit
from clients.deribit import DeribitError
from shared.cache import TTLCache
from shared.quotes import prepare_oi_chain, prepare_otm_quotes

logger = logging.getLogger(__name__)

# Prepared tables are memoized so the per-request builders in one refresh window
# share a single quotes pass instead of each re-parsing the whole option chain.
# TTL matches the upstream book cache.
_cache = TTLCache(settings.cache_ttl_seconds)


def validate_currency(currency: str) -> str:
    cur = currency.upper()
    if cur not in settings.supported_currency_list:
        logger.warning("rejected due to unsupported currency=%s", cur)
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported currency '{currency}'. Supported: {settings.supported_currency_list}",
        )
    return cur


def load_spot(cur: str) -> float:
    try:
        return deribit.fetch_spot(cur)
    except DeribitError as exc:
        logger.warning("cannot fetch spot for currency=%s, %s", cur, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def load_market_data(cur: str) -> tuple[float, list[dict]]:
    try:
        spot = deribit.fetch_spot(cur)
        summaries = deribit.fetch_option_summaries(cur)
    except DeribitError as exc:
        logger.warning("cannot fetch upstream data for currency=%s, %s", cur, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return spot, summaries


def load_otm_quotes(cur: str) -> tuple[float, pd.DataFrame]:
    """Spot and the prepared OTM quote table for ``cur``, memoized by currency.

    The returned DataFrame is shared across callers within the TTL and must be treated as read-only.
    """

    def producer() -> tuple[float, pd.DataFrame]:
        spot, summaries = load_market_data(cur)
        return spot, prepare_otm_quotes(summaries, spot)

    return _cache.get_or_compute(f"prepared:{cur}", producer)


def load_oi_chain(cur: str) -> tuple[float, pd.DataFrame]:
    """Spot and the prepared full-chain open-interest table for ``cur``, memoized by currency.

    The returned DataFrame is shared across callers within the TTL and must be treated as read-only.
    """

    def producer() -> tuple[float, pd.DataFrame]:
        spot, summaries = load_market_data(cur)
        return spot, prepare_oi_chain(summaries, spot)

    return _cache.get_or_compute(f"oi_prepared:{cur}", producer)
