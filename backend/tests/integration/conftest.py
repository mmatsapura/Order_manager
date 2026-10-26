import os
import socket
import uuid
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.db import MongoDB
from app.db.redis import RedisDB
from app.main import app
from app.models.product import Product
from app.queue.connection import RabbitMQ
from app.repositories.product import ProductRepository


MONGO_URL = os.getenv("TEST_MONGODB_URL", "mongodb://admin:password123@localhost:27017/?authSource=admin")
RABBIT_URL = os.getenv("TEST_RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/0")

SERVICES = {"MongoDB": (MONGO_URL, 27017), "RabbitMQ": (RABBIT_URL, 5672), "Redis": (REDIS_URL, 6379)}


def pytest_collection_modifyitems(items):
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


def is_reachable(url: str, default_port: int) -> bool:
    parsed = urlparse(url)
    try:
        with socket.create_connection((parsed.hostname, parsed.port or default_port), timeout=1):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def unavailable_services() -> list[str]:
    return [name for name, (url, port) in SERVICES.items() if not is_reachable(url, port)]


@pytest.fixture
async def stack(monkeypatch, unavailable_services):
    if unavailable_services:
        pytest.skip(
            f"{', '.join(unavailable_services)} unavailable. "
            "Start them with: docker compose up -d mongo redis rabbitmq"
        )

    suffix = uuid.uuid4().hex[:8]
    db_name = f"order_manager_test_{suffix}"
    queue_name = f"orders_test_{suffix}"
    # every test gets its own queue, so a running worker or other tests never see these messages
    monkeypatch.setattr("app.queue.connection.QUEUE_NAME", queue_name)
    monkeypatch.setattr("app.queue.producer.QUEUE_NAME", queue_name)

    mongo = MongoDB(MONGO_URL, db_name)
    rabbit = RabbitMQ(RABBIT_URL)
    redis = RedisDB(REDIS_URL)
    await mongo.connect()
    await rabbit.connect()
    await redis.connect()

    app.state.mongo = mongo
    app.state.rabbit = rabbit
    app.state.redis = redis
    try:
        yield SimpleNamespace(mongo=mongo, rabbit=rabbit, redis=redis, db=mongo.db)
    finally:
        await mongo.client.drop_database(db_name)
        await mongo.close()
        await rabbit.close()
        await redis.close()
        await delete_queue()


async def delete_queue() -> None:
    cleaner = RabbitMQ(RABBIT_URL)
    await cleaner.connect()
    await cleaner.queue.delete(if_unused=False, if_empty=False)
    await cleaner.close()


@pytest.fixture
async def client(stack):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http


@pytest.fixture
async def product(stack):
    return await ProductRepository(stack.db).create_product(Product(name="Tea", price=5))


@pytest.fixture
async def token(client):
    await client.post("/auth/register", json={"email": "user@example.com", "password": "secret1"})
    response = await client.post("/auth/login", json={"email": "user@example.com", "password": "secret1"})
    return response.json()["access_token"]
