import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.config import settings
from app.models.notification import NotificationType
from app.models.order import OrderStatus
from app.schemas.queue import QueueMessage
from app.services.queue_processing import QueueProcessingService
from tests.factories import make_order


@pytest.fixture(autouse=True)
def fast_worker(monkeypatch):
    monkeypatch.setattr(settings, "processing_delay_seconds", 0)
    monkeypatch.setattr(settings, "max_retries", 3)


@pytest.fixture
def order_repo():
    return AsyncMock()


@pytest.fixture
def notifications():
    return AsyncMock()


@pytest.fixture
def worker(order_repo, notifications):
    return QueueProcessingService(order_repo, notifications, object(), AsyncMock())


@pytest.fixture
def publish(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.services.queue_processing.publish_order", mock)
    return mock


@pytest.fixture
def failing_work(monkeypatch):
    async def fail(_seconds):
        raise RuntimeError("boom")

    # replace asyncio only inside the worker module, not globally
    monkeypatch.setattr(
        "app.services.queue_processing.asyncio",
        SimpleNamespace(sleep=fail, CancelledError=asyncio.CancelledError),
    )


def message(attempt=0):
    return QueueMessage(order_id="o1", attempt=attempt).model_dump_json().encode()


def saved_statuses(order_repo):
    return [call.kwargs["status"] for call in order_repo.update_order.await_args_list]


async def test_invalid_message_is_ignored(worker, order_repo):
    await worker.handle(b"not-json")

    order_repo.get_order_by_id.assert_not_called()


async def test_missing_order_is_skipped(worker, order_repo):
    order_repo.get_order_by_id.return_value = None

    await worker.handle(message())

    order_repo.update_order.assert_not_called()


async def test_cancelled_order_is_skipped(worker, order_repo):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.CANCELLED)

    await worker.handle(message())

    order_repo.update_order.assert_not_called()


async def test_worker_completes_order(worker, order_repo, notifications):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.QUEUED)

    await worker.handle(message())

    assert saved_statuses(order_repo) == [OrderStatus.PROCESSING, OrderStatus.COMPLETED]
    saved = notifications.create_notification.await_args.args[0]
    assert saved.type == NotificationType.ORDER_COMPLETED


async def test_cancel_during_processing_does_not_complete(worker, order_repo, notifications):
    order_repo.get_order_by_id.side_effect = [
        make_order(status=OrderStatus.QUEUED),
        make_order(status=OrderStatus.CANCELLED),
    ]

    await worker.handle(message())

    assert saved_statuses(order_repo) == [OrderStatus.PROCESSING]
    notifications.create_notification.assert_not_called()


async def test_failure_requeues_until_limit(worker, order_repo, publish, failing_work):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.QUEUED)

    await worker.handle(message(attempt=0))

    publish.assert_awaited_once_with(worker.rabbit, "o1", attempt=1)
    last_update = order_repo.update_order.await_args
    assert last_update.kwargs["status"] == OrderStatus.QUEUED
    assert last_update.kwargs["retry_count"] == 1
    assert last_update.kwargs["error_message"] == "boom"


async def test_failure_after_retry_limit_marks_failed(worker, order_repo, notifications, publish, failing_work):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.PROCESSING)

    await worker.handle(message(attempt=2))

    publish.assert_not_called()
    last_update = order_repo.update_order.await_args
    assert last_update.kwargs["status"] == OrderStatus.FAILED
    assert last_update.kwargs["retry_count"] == 3
    saved = notifications.create_notification.await_args.args[0]
    assert saved.type == NotificationType.ORDER_FAILED
    assert saved.message == "boom"
