import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_get(key: str) -> str | None:
    return redis_client.get(key)

def cache_set(key: str, value: str, ttl: int = 300):
    redis_client.set(key, value, ex=ttl)

def cache_delete(key: str):
    redis_client.delete(key)