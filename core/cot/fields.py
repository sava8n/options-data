"""Contract codes, participant categories, and the verified Socrata field map."""

from __future__ import annotations

DATE_FIELD = "report_date_as_yyyy_mm_dd"
CODE_FIELD = "cftc_contract_market_code"
OI_FIELD = "open_interest_all"

# BTC per contract: CME Bitcoin (5 BTC) and Micro Bitcoin (0.1 BTC)
BITCOIN_CODE = "133741"
MICRO_BITCOIN_CODE = "133742"
CONTRACT_WEIGHTS: dict[str, float] = {BITCOIN_CODE: 5.0, MICRO_BITCOIN_CODE: 0.1}

# fixed display order
CATEGORIES: tuple[str, ...] = ("dealer", "asset_mgr", "lev_money", "other_rept", "nonrept")

LABELS: dict[str, str] = {
    "dealer": "DEALER",
    "asset_mgr": "ASSET MGR",
    "lev_money": "LEV FUNDS",
    "other_rept": "OTHER REPT",
    "nonrept": "NONREPT",
}

# category -> side -> Socrata field; None where the report has no such series
POSITION_FIELDS: dict[str, dict[str, str | None]] = {
    "dealer": {
        "long": "dealer_positions_long_all",
        "short": "dealer_positions_short_all",
        "spread": "dealer_positions_spread_all",
    },
    "asset_mgr": {
        "long": "asset_mgr_positions_long",
        "short": "asset_mgr_positions_short",
        "spread": "asset_mgr_positions_spread",
    },
    "lev_money": {
        "long": "lev_money_positions_long",
        "short": "lev_money_positions_short",
        "spread": "lev_money_positions_spread",
    },
    "other_rept": {
        "long": "other_rept_positions_long",
        "short": "other_rept_positions_short",
        "spread": "other_rept_positions_spread",
    },
    "nonrept": {
        "long": "nonrept_positions_long_all",
        "short": "nonrept_positions_short_all",
        "spread": None,
    },
}

# CFTC reports no trader counts for non-reportables
TRADER_FIELDS: dict[str, dict[str, str | None]] = {
    "dealer": {"long": "traders_dealer_long_all", "short": "traders_dealer_short_all"},
    "asset_mgr": {"long": "traders_asset_mgr_long_all", "short": "traders_asset_mgr_short_all"},
    "lev_money": {"long": "traders_lev_money_long_all", "short": "traders_lev_money_short_all"},
    "other_rept": {"long": "traders_other_rept_long_all", "short": "traders_other_rept_short"},
    "nonrept": {"long": None, "short": None},
}
