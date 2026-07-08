"""CFTC public reporting (Socrata) API client."""

from __future__ import annotations

import logging
import time

import certifi
import requests

logger = logging.getLogger(__name__)

CFTC_API = "https://publicreporting.cftc.gov/resource"
TFF_FUTURES_ONLY = "gpe5-46if"
HTTP_TIMEOUT = 20


class CftcError(RuntimeError):
    """Raised when a CFTC request fails or returns an unexpected payload."""


def fetch_tff_history(codes: tuple[str, ...]) -> list[dict]:
    """All weekly TFF futures-only records for ``codes``, date-ascending."""
    quoted = ",".join(f"'{code}'" for code in codes)
    start = time.perf_counter()
    try:
        resp = requests.get(
            f"{CFTC_API}/{TFF_FUTURES_ONLY}.json",
            params={
                "$where": f"cftc_contract_market_code in({quoted})",
                "$order": "report_date_as_yyyy_mm_dd",
                "$limit": "50000",
            },
            timeout=HTTP_TIMEOUT,
            verify=certifi.where(),
        )
        resp.raise_for_status()
        records = resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("CFTC request failed: %s", exc)
        raise CftcError(f"CFTC request failed: {exc}") from exc
    if not isinstance(records, list):
        raise CftcError(f"CFTC returned unexpected payload: {type(records).__name__}")
    logger.info("fetched %d TFF records in %.0f ms", len(records), (time.perf_counter() - start) * 1000)
    return records
