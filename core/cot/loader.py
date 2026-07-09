"""Cached loading of the COT state.

One state per currency behind a long TTL: a weekly-cadence feed needs one CFTC
round-trip per window to serve every endpoint. A failed refresh keeps serving the
previous state and the price-overlay fetch is best-effort.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from fastapi import HTTPException

from clients import cftc, deribit
from clients.cftc import CftcError
from clients.deribit import DeribitError
from config import settings
from cot import prices
from cot.contracts import COT_SPECS, CotSpec
from cot.normalize import build as normalize
from cot.state import CotState
from shared.cache import TTLCache

logger = logging.getLogger(__name__)

_cache = TTLCache(settings.cot_cache_ttl_seconds)

_CHUNK_MS = 1000 * 86_400_000  # stay under any per-request bar cap


def _fetch_price_candles(prev: dict | None, spec: CotSpec) -> dict | None:
    try:
        end_ms = int(time.time() * 1000)
        prev_ticks = (prev or {}).get("ticks") or []
        start = int(prev_ticks[-1]) if prev_ticks else spec.price_start_ms
        chunks = []
        while start < end_ms:
            stop = min(start + _CHUNK_MS, end_ms)
            chunks.append(deribit.fetch_instrument_history(spec.price_instrument, start, stop))
            start = stop
        return prices.splice(prev, chunks)
    except DeribitError as exc:
        logger.warning("keeping stale COT price candles for currency=%s, %s", spec.currency, exc)
        return prev


def load_cot_state(cur: str) -> CotState:
    spec = COT_SPECS[cur]

    def refresh(prev: CotState | None) -> CotState:
        try:
            tidy = normalize(cftc.fetch_tff_history(tuple(spec.weights)))
        except (CftcError, ValueError) as exc:
            if prev is not None:
                logger.warning("keeping stale COT state for currency=%s, %s", cur, exc)
                return prev
            logger.warning("cannot fetch COT data for currency=%s, %s", cur, exc)
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return CotState(
            as_of=datetime.now(timezone.utc),
            spec=spec,
            tidy=tidy,
            price_candles=_fetch_price_candles(prev.price_candles if prev else None, spec),
        )

    return _cache.get_or_refresh(f"cot:{cur}", refresh)


def warm_up() -> None:
    """Best-effort pre-load at startup; failures log and never block boot."""
    start = time.perf_counter()
    for cur in settings.supported_currency_list:
        try:
            load_cot_state(cur)
        except Exception as exc:
            logger.warning("COT warm-up failed for currency=%s, %s", cur, exc)
    logger.info("COT warm-up complete in %.0f ms", (time.perf_counter() - start) * 1000)
