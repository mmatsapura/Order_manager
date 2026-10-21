from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self._uri = uri
        self._db_name = db_name
        self._client = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncMongoClient(self._uri)
        await self._ensure_indexes()

    async def _ensure_indexes(self) -> None:
        await self.db["users"].create_index("email", unique=True)
        await self.db["orders"].create_index("order_id", unique=True)
        await self.db["products"].create_index("name", unique=True)
        await self.db["orders"].create_index("status")
        await self.db["orders"].create_index("customer_email")
        await self.db["orders"].create_index("created_at")
        await self.db["notifications"].create_index("order_id")
        await self.db["order_events"].create_index("order_id")

    async def close(self) -> None:
        if self._client is None:
            return
        await self._client.close()
        self._client = None

    @property
    def client(self) -> AsyncMongoClient:
        if self._client is None:
            raise RuntimeError("No connection to MongoDB")
        return self._client

    @property
    def db(self) -> AsyncDatabase:
        return self.client[self._db_name]

    async def ping(self) -> None:
        await self.client.admin.command("ping")
