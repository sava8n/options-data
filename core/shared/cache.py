"""In-memory TTL cache with per-key locks to collapse concurrent misses.

Fast lock-free freshness read, then a per-key lock around the (expensive)
producer so that when several callers miss the same key at once only one computes
it and the rest reuse the result - no thundering herd. Expired entries are kept
and handed to the producer so it can refresh incrementally instead of rebuilding
from scratch.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

_T = TypeVar("_T")


class TTLCache:
    """Thread-safe cache whose entries expire ``ttl_seconds`` after they are stored."""

    def __init__(self, ttl_seconds: float) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}
        self._store_lock = threading.Lock()
        # per-key locks serialize concurrent misses so only one caller computes a key
        self._key_locks: dict[str, threading.Lock] = {}
        self._key_locks_guard = threading.Lock()

    def _lock_for(self, key: str) -> threading.Lock:
        with self._key_locks_guard:
            lock = self._key_locks.get(key)
            if lock is None:
                lock = threading.Lock()
                self._key_locks[key] = lock
            return lock

    def _read_fresh(self, key: str) -> tuple[bool, Any]:
        with self._store_lock:
            entry = self._store.get(key)
            if entry is not None and time.monotonic() - entry[0] < self._ttl:
                return True, entry[1]
        return False, None

    def get_or_refresh(self, key: str, refresh: Callable[[Optional[_T]], _T]) -> _T:
        """Return the fresh cached value for ``key``, else refresh, store and return it.

        ``refresh`` receives the previous (expired) value — ``None`` on first build —
        so producers can update incrementally.
        """
        hit, value = self._read_fresh(key)
        if hit:
            logger.debug("cache hit for key=%s", key)
            return value

        with self._lock_for(key):
            # another caller may have populated the cache while we waited for the lock
            hit, value = self._read_fresh(key)
            if hit:
                logger.debug("cache hit for key=%s (filled while waiting)", key)
                return value

            with self._store_lock:
                entry = self._store.get(key)
            prev = entry[1] if entry is not None else None

            logger.debug("cache miss for key=%s, refreshing", key)
            value = refresh(prev)
            with self._store_lock:
                self._store[key] = (time.monotonic(), value)
            return value
