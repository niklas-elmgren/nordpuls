"""
In-memory TTL cache for API responses.
"""

from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json


_cache: dict = {}


def ttl_cache(seconds: int):
    """Decorator that caches function results with a time-to-live."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{hashlib.md5(json.dumps((args, kwargs), default=str).encode()).hexdigest()}"
            if key in _cache:
                result, expiry = _cache[key]
                if datetime.now() < expiry:
                    return result
            result = func(*args, **kwargs)
            _cache[key] = (result, datetime.now() + timedelta(seconds=seconds))
            return result
        return wrapper
    return decorator


def clear_cache():
    """Clear all cached entries."""
    _cache.clear()


def clear_expired():
    """Remove expired entries from cache."""
    now = datetime.now()
    expired = [k for k, (_, exp) in _cache.items() if now >= exp]
    for k in expired:
        del _cache[k]
