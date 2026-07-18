"""Settings parsers for the comma-separated env fields."""

from __future__ import annotations

from config import Settings


def test_cors_origin_list_splits_and_strips():
    settings = Settings(cors_origins="  http://a.com , http://b.com ,")
    assert settings.cors_origin_list == ["http://a.com", "http://b.com"]


def test_supported_currency_list_uppercases():
    settings = Settings(supported_currencies="btc, eth ,")
    assert settings.supported_currency_list == ["BTC", "ETH"]
