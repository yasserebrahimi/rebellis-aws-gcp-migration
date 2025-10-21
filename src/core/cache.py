import logging, json
from typing import Any, Optional

from src.core.config import settings
logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
except Exception:
    redis = None

class RedisCache:
    def __init__(self):
        self.redis_client: Optional['redis.Redis'] = None
        self.ttl = settings.CACHE_TTL

    async def initialize(self):
        if redis is None:
            logger.warning("redis-py not installed; cache disabled")
            self.redis_client = None
            return
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis ready")
        except Exception as e:
            logger.warning("Redis disabled: %s", e)
            self.redis_client = None

    async def get(self, key: str):
        if not self.redis_client: return None
        try:
            v = await self.redis_client.get(key)
            return json.loads(v) if v else None
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.redis_client: return False
        try:
            await self.redis_client.setex(key, ttl or self.ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.redis_client: return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")
            return False

    async def clear(self) -> bool:
        if not self.redis_client: return False
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}")
            return False

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()

redis_client = RedisCache()
