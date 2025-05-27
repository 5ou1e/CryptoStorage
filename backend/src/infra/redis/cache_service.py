import asyncio
import json
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis


class RedisCacheService:
    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, expire: int = 600):
        await self._redis.setex(key, expire, json.dumps(value))

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def clear_all(self):
        """Очищает весь кеш (осторожно!)"""
        await self._redis.flushdb()
