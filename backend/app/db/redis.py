from redis.asyncio import Redis


class RedisDB:
    def __init__(self, url: str):
        self.url = url
        self._client = None

    async def connect(self):
        self._client = Redis.from_url(self.url, decode_responses=True)
        await self.ping()
        return

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError('Redis is not connected')
        return self._client

    async def ping(self):
        await self.client.ping()
        return

    async def blacklist(self, jti: str, ttl_seconds: int) -> None:
        if ttl_seconds > 0:
            await self.client.set(f'jwt:blacklist:{jti}', '1', ex=ttl_seconds)
            return
        return

    async def is_blacklisted(self, jti: str) -> bool:
        return await self.client.exists(f'jwt:blacklist:{jti}') == 1

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            return
        return
