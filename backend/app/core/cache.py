import logging
from redis import asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize asynchronous Redis client
redis_client = aioredis.from_url(settings.REDIS_URL,encoding="utf-8",decode_responses=True)

async def cache_get(key: str) -> str | None:
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.error("Redis get failed", extra={"error": str(e)})
        return None

async def cache_set(key: str, value: str, ttl: int = 300):
    try:
        await redis_client.set(key, value, ex=ttl)
    except Exception as e:
        logger.error("Redis set failed", extra={"error": str(e)})

async def cache_delete(key: str) -> bool:
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error("Redis delete failed", extra={"error": str(e)})
        return False