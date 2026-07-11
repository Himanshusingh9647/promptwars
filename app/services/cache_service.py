"""
TTL-based caching utilities.

Provides a thread-safe, time-to-live cache decorator that can be
applied to any function. Unlike ``functools.lru_cache``, entries
automatically expire after the configured TTL.
"""

import threading
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from app.utils.constants import DEFAULT_CACHE_MAX_SIZE, DEFAULT_CACHE_TTL_SECONDS

F = TypeVar("F", bound=Callable[..., Any])


class TTLCache:
    """
    A simple thread-safe cache with time-to-live expiration.

    Attributes:
        ttl: Time-to-live in seconds for each cache entry.
        max_size: Maximum number of entries before eviction.
    """

    def __init__(
        self,
        ttl: int = DEFAULT_CACHE_TTL_SECONDS,
        max_size: int = DEFAULT_CACHE_MAX_SIZE,
    ) -> None:
        self.ttl: int = ttl
        self.max_size: int = max_size
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock: threading.Lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """
        Retrieve a value from the cache if it exists and hasn't expired.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found or expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            value, timestamp = entry
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache with the current timestamp.

        Evicts the oldest entry if the cache exceeds max_size.

        Args:
            key: The cache key.
            value: The value to store.
        """
        with self._lock:
            # Evict oldest entry if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
            self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        """Return the current number of entries in the cache."""
        with self._lock:
            return len(self._cache)


def ttl_cache(
    ttl: int = DEFAULT_CACHE_TTL_SECONDS,
    max_size: int = DEFAULT_CACHE_MAX_SIZE,
) -> Callable[[F], F]:
    """
    Decorator that caches function results with TTL expiration.

    Args:
        ttl: Time-to-live in seconds.
        max_size: Maximum cache entries.

    Returns:
        Decorated function with caching behaviour.

    Example::

        @ttl_cache(ttl=60)
        def get_weather(location: str) -> dict:
            ...
    """
    cache = TTLCache(ttl=ttl, max_size=max_size)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build a deterministic cache key from arguments
            key_parts = [str(a) for a in args]
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{func.__name__}:{'|'.join(key_parts)}"

            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # Expose cache for testing
        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
