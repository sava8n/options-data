"""Currency validation shared by every currency-scoped route."""

from __future__ import annotations

import logging

from fastapi import HTTPException

from config import settings

logger = logging.getLogger(__name__)


def validate_currency(currency: str) -> str:
    cur = currency.upper()
    if cur not in settings.supported_currency_list:
        logger.warning("rejected due to unsupported currency=%s", cur)
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported currency '{currency}'. Supported: {settings.supported_currency_list}",
        )
    return cur
