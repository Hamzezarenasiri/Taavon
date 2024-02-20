from typing import Any

import redis.asyncio as aredis
from tenacity import retry, stop_after_attempt, wait_exponential

from src.services.cache.base import BaseCache

retry_policy = retry(
    reraise=True,
    wait=wait_exponential(min=1),
    stop=stop_after_attempt(5),
)


class Redis(BaseCache):
    def __init__(self):
        self._client = None

    async def connect(
        self,
        host: str,
        port: int = None,
        db: int = None,
        password: str = None,
        timeout: int = None,
    ):
        params = {"host": host}
        if port is not None:
            params["port"] = port
        if db is not None:
            params["db"] = db
        if password is not None:
            params["password"] = password
        if timeout is not None:
            params["socket_timeout"] = timeout

        self._client = aredis.StrictRedis(**params)

    @retry_policy
    async def flushdb(self):
        return await self._client.flushdb()

    @retry_policy
    async def set(self, key: str, value: Any, expiry: int = None):
        return await self._client.set(key, value, ex=expiry)

    @retry_policy
    async def get(self, key: str) -> bytes:
        return await self._client.get(key)

    @retry_policy
    async def exists(self, key: str) -> bool:
        return await self._client.exists(key)

    @retry_policy
    async def incrby(self, key: str, by: int = 1):
        return await self._client.incrby(key, by)

    @retry_policy
    async def decrby(self, key: str, by: int = 1):
        return await self._client.decr(key, by)

    @retry_policy
    async def hmset(self, key: str, *field_values):
        assert len(field_values) % 2 == 0

        mapping = dict(zip(field_values[::2], field_values[1::2]))
        return await self._client.hmset(key, mapping)

    @retry_policy
    async def hmget(self, key: str, *fields):
        return await self._client.hmget(key, fields)

    @retry_policy
    async def hgetall(self, key: str):
        return await self._client.hgetall(key)

    @retry_policy
    async def hkeys(self, key: str):
        return await self._client.hkeys(key)

    @retry_policy
    async def info(self):
        return await self._client.info()

    @retry_policy
    async def keys(self, pattern="*"):
        return await self._client.keys(pattern)

    @retry_policy
    async def rpush(self, key: str, *elements):
        return await self._client.rpush(key, *elements)

    @retry_policy
    async def lpush(self, key: str, *elements):
        return await self._client.lpush(key, *elements)

    @retry_policy
    async def rpop(self, key: str):
        return await self._client.rpop(key)

    @retry_policy
    async def lpop(self, key: str):
        return await self._client.lpop(key)

    @retry_policy
    async def ping(self):
        return await self._client.ping()

    @retry_policy
    async def ttl(self, key):
        return await self._client.ttl(key)

    @retry_policy
    async def delete(self, key):
        return await self._client.delete(key)
