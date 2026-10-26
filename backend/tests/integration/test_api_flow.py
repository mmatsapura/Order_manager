import asyncio
from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.core.security import verify_password
from app.repositories.notification import NotificationRepository
from app.repositories.order import OrderRepository
from app.repositories.order_event import OrderEventRepository
from app.repositories.user import UserRepository
from app.schemas.queue import QueueMessage
from app.services.queue_processing import QueueProcessingService


def auth(token):
    return {"Authorization": f"Bearer {token}"}


async def place_order(client, token, product_id, quantity=1):
    return await client.post(
        "/orders",
        headers=auth(token),
        json={
            "customer_name": "Ann",
            "customer_email": "ann@example.com",
            "items": [{"product_id": product_id, "quantity": quantity}],
        },
    )


async def run_worker(stack) -> list[QueueMessage]:
    """Take messages from the real RabbitMQ queue and process them until it is empty."""
    worker = QueueProcessingService(
        OrderRepository(stack.db),
        NotificationRepository(stack.db),
        stack.rabbit,
        OrderEventRepository(stack.db),
    )
    handled = []
    while True:
        message = await stack.rabbit.queue.get(fail=False, timeout=5)
        if message is None:
            return handled
        handled.append(QueueMessage.model_validate_json(message.body))
        await worker.handle(message.body)
        await message.ack()


def break_processing(monkeypatch, action):
    # replace asyncio only inside the worker module, so aio-pika keeps working
    monkeypatch.setattr(
        "app.services.queue_processing.asyncio",
        SimpleNamespace(sleep=action, CancelledError=asyncio.CancelledError),
    )


@pytest.fixture(autouse=True)
def fast_worker(monkeypatch):
    monkeypatch.setattr(settings, "processing_delay_seconds", 0)
    monkeypatch.setattr(settings, "max_retries", 3)


async def test_auth_flow(client, stack):
    created = await client.post("/auth/register", json={"email": "ann@example.com", "password": "secret1"})
    assert created.status_code == 201

    saved = await UserRepository(stack.db).get_user_by_email("ann@example.com")
    assert verify_password("secret1", saved.hashed_password)

    duplicate = await client.post("/auth/register", json={"email": "ann@example.com", "password": "secret1"})
    assert duplicate.status_code == 409

    bad_login = await client.post("/auth/login", json={"email": "ann@example.com", "password": "wrong-pass"})
    assert bad_login.status_code == 401

    logged_in = await client.post("/auth/login", json={"email": "ann@example.com", "password": "secret1"})
    assert logged_in.status_code == 200
    token = logged_in.json()["access_token"]

    assert (await client.get("/orders")).status_code == 401
    assert (await client.get("/orders", headers=auth(token))).status_code == 200

    logged_out = await client.post("/auth/logout", headers=auth(token))
    assert logged_out.status_code == 204
    assert (await client.get("/orders", headers=auth(token))).status_code == 401


async def test_inactive_user_cannot_login(client, stack):
    await client.post("/auth/register", json={"email": "off@example.com", "password": "secret1"})
    await stack.db["users"].update_one({"email": "off@example.com"}, {"$set": {"is_active": False}})

    response = await client.post("/auth/login", json={"email": "off@example.com", "password": "secret1"})

    assert response.status_code == 401


async def test_order_is_saved_queued_and_completed(client, stack, product, token):
    response = await place_order(client, token, product.id, quantity=2)
    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "Queued"
    assert order["total_price"] == 10

    in_mongo = await OrderRepository(stack.db).get_order_by_id(order["order_id"])
    assert in_mongo.status.value == "Queued"

    handled = await run_worker(stack)
    assert [(m.order_id, m.attempt) for m in handled] == [(order["order_id"], 0)]

    completed = await client.get(f"/orders/{order['order_id']}", headers=auth(token))
    assert completed.json()["status"] == "Completed"

    notes = await client.get(f"/orders/{order['order_id']}/notifications", headers=auth(token))
    assert [note["type"] for note in notes.json()] == ["Order Completed"]
    events = await client.get(f"/orders/{order['order_id']}/events", headers=auth(token))
    assert [event["to_status"] for event in events.json()] == ["Created", "Queued", "Processing", "Completed"]


async def test_unknown_product_and_list_filters(client, product, token):
    unknown = await place_order(client, token, "missing")
    assert unknown.status_code == 400

    created = await place_order(client, token, product.id)
    assert created.status_code == 201

    queued = await client.get("/orders", headers=auth(token), params={"status": "Queued", "email": "ann"})
    assert queued.json()["total"] == 1
    failed = await client.get("/orders", headers=auth(token), params={"status": "Failed"})
    assert failed.json()["total"] == 0
    assert (await client.get("/orders/missing-order", headers=auth(token))).status_code == 404


async def test_queue_down_marks_order_failed(client, stack, product, token):
    await stack.rabbit.close()

    response = await place_order(client, token, product.id)

    assert response.status_code == 503
    listed = await client.get("/orders", headers=auth(token))
    assert listed.json()["items"][0]["status"] == "Failed"


async def test_worker_retries_then_completes(client, stack, product, token, monkeypatch):
    attempts = []

    async def fail_first_time(_seconds):
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("boom")

    break_processing(monkeypatch, fail_first_time)
    order_id = (await place_order(client, token, product.id)).json()["order_id"]

    handled = await run_worker(stack)

    assert [m.attempt for m in handled] == [0, 1]
    order = (await client.get(f"/orders/{order_id}", headers=auth(token))).json()
    assert order["status"] == "Completed"
    assert order["retry_count"] == 1


async def test_worker_fails_after_retry_limit(client, stack, product, token, monkeypatch):
    async def always_fail(_seconds):
        raise RuntimeError("boom")

    break_processing(monkeypatch, always_fail)
    order_id = (await place_order(client, token, product.id)).json()["order_id"]

    handled = await run_worker(stack)

    assert [m.attempt for m in handled] == [0, 1, 2]
    order = (await client.get(f"/orders/{order_id}", headers=auth(token))).json()
    assert order["status"] == "Failed"
    assert order["retry_count"] == 3
    notes = await client.get(f"/orders/{order_id}/notifications", headers=auth(token))
    assert [note["type"] for note in notes.json()] == ["Order Failed"]


async def test_cancel_while_processing_skips_completion(client, stack, product, token, monkeypatch):
    order_id = (await place_order(client, token, product.id)).json()["order_id"]

    async def cancel_during_work(_seconds):
        response = await client.post(f"/orders/{order_id}/cancel", headers=auth(token))
        assert response.status_code == 200

    break_processing(monkeypatch, cancel_during_work)
    await run_worker(stack)

    order = (await client.get(f"/orders/{order_id}", headers=auth(token))).json()
    assert order["status"] == "Cancelled"
    notes = await client.get(f"/orders/{order_id}/notifications", headers=auth(token))
    assert [note["type"] for note in notes.json()] == ["Order Cancelled"]


async def test_failed_order_can_be_requeued_manually(client, stack, product, token, monkeypatch):
    async def always_fail(_seconds):
        raise RuntimeError("boom")

    monkeypatch.setattr(settings, "max_retries", 1)
    break_processing(monkeypatch, always_fail)
    order_id = (await place_order(client, token, product.id)).json()["order_id"]

    blocked = await client.patch(f"/orders/{order_id}", headers=auth(token), json={"status": "Completed"})
    assert blocked.status_code == 409

    await run_worker(stack)
    failed = await client.get(f"/orders/{order_id}", headers=auth(token))
    assert failed.json()["status"] == "Failed"

    requeued = await client.patch(f"/orders/{order_id}", headers=auth(token), json={"status": "Queued"})
    assert requeued.status_code == 200
    assert requeued.json()["status"] == "Queued"

    break_processing(monkeypatch, asyncio.sleep)
    handled = await run_worker(stack)
    assert [m.attempt for m in handled] == [0]
    done = await client.get(f"/orders/{order_id}", headers=auth(token))
    assert done.json()["status"] == "Completed"


async def test_completed_order_cannot_be_cancelled(client, stack, product, token):
    order_id = (await place_order(client, token, product.id)).json()["order_id"]
    await run_worker(stack)

    response = await client.post(f"/orders/{order_id}/cancel", headers=auth(token))

    assert response.status_code == 409


async def test_health(client, stack):
    ok = await client.get("/health")
    assert ok.json() == {
        "status": "ok",
        "api": "ok",
        "mongodb": "ok",
        "rabbitmq": "ok",
        "redis": "ok",
    }

    await stack.redis.close()
    await stack.rabbit.close()
    degraded = (await client.get("/health")).json()

    assert degraded["status"] == "error"
    assert degraded["api"] == "ok"
    assert degraded["mongodb"] == "ok"
    assert degraded["rabbitmq"] == "error"
    assert degraded["redis"] == "error"
