"""TTLCache behaviour: miss populates, hit within TTL reuses, expiry refreshes with prev value."""

from __future__ import annotations

import shared.cache as cache_mod
from shared.cache import TTLCache


def test_miss_then_hit_then_expiry(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(cache_mod.time, "monotonic", lambda: clock[0])

    seen_prev = []

    def refresh(prev):
        seen_prev.append(prev)
        return f"v{len(seen_prev)}"

    cache = TTLCache(ttl_seconds=10)

    # first call: miss -> refresh(None)
    assert cache.get_or_refresh("k", refresh) == "v1"
    assert seen_prev == [None]

    # within TTL: hit -> refresh not called again
    assert cache.get_or_refresh("k", refresh) == "v1"
    assert len(seen_prev) == 1

    # past TTL: miss -> refresh receives the previous (expired) value
    clock[0] = 1011.0
    assert cache.get_or_refresh("k", refresh) == "v2"
    assert seen_prev[-1] == "v1"
