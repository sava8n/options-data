"""Per-currency COT markets: the CFTC contracts behind a currency and its price overlay."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CotSpec:
    currency: str
    weights: dict[str, float]  # CFTC contract market code -> base units per contract
    micro_code: str  # its first appearance dates the micro listing
    price_instrument: str  # Deribit instrument for the price overlay
    price_start_ms: int  # first report era for this market


BTC = CotSpec(
    currency="BTC",
    # CME Bitcoin (5 BTC) and Micro Bitcoin (0.1 BTC)
    weights={"133741": 5.0, "133742": 0.1},
    micro_code="133742",
    price_instrument="BTC-PERPETUAL",
    price_start_ms=1_512_086_400_000,  # 2017-12-01
)

# must carry an entry for every currency in settings.supported_currencies
COT_SPECS: dict[str, CotSpec] = {BTC.currency: BTC}
