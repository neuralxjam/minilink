import os

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "86400"))  # seconds; 24 h default

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def cache_get(code: str) -> str | None:
    return get_redis().get(f"link:{code}")


def cache_set(code: str, url: str) -> None:
    get_redis().set(f"link:{code}", url, ex=CACHE_TTL)


def cache_del(code: str) -> None:
    get_redis().delete(f"link:{code}")
