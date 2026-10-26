import pytest
from unittest.mock import AsyncMock

from app.core.exceptions import (
    OrderCanNotBeCancelled,
    OrderCannotBeUpdated,
    OrderNotFound,
    ProductNotFound,
    QueueUnavailable,
)
from app.models.notification import NotificationType
from app.models.order import OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderListQuery, OrderUpdate
from app.services.order import OrderService
from tests.factories import make_order


@pytest.fixture
def order_repo():
    return AsyncMock()


@pytest.fixture
def notification_repo():
    return AsyncMock()


@pytest.fixture
def product_repo():
    repo = AsyncMock()
    repo.get_product_by_id.return_value = Product(id="p1", name="Tea", price=10)
    return repo


@pytest.fixture
def service(order_repo, notification_repo, product_repo):
    return OrderService(
        order_repo=order_repo,
        notification_repo=notification_repo,
        product_repo=product_repo,
        rabbit=object(),
        order_event_repo=AsyncMock(),
    )


@pytest.fixture
def order_body():
    return OrderCreate(
        customer_name="Ann",
        customer_email="ann@example.com",
        items=[{"product_id": "p1", "quantity": 2}],
    )


@pytest.fixture
def publish(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.services.order.publish_order", mock)
    return mock


async def test_create_order_sums_price_and_queues(service, order_repo, publish, order_body):
    order = await service.create_order(order_body)

    assert order.status == OrderStatus.QUEUED
    assert order.total_price == 20
    publish.assert_awaited_once_with(service.rabbit, order.order_id, attempt=0)
    order_repo.update_order.assert_awaited_with(order.order_id, status=OrderStatus.QUEUED)


async def test_create_order_unknown_product(service, product_repo, publish, order_body):
    product_repo.get_product_by_id.return_value = None

    with pytest.raises(ProductNotFound):
        await service.create_order(order_body)
    publish.assert_not_called()


async def test_create_order_marks_failed_when_queue_is_down(service, order_repo, publish, order_body):
    publish.side_effect = RuntimeError("down")

    with pytest.raises(QueueUnavailable):
        await service.create_order(order_body)

    failed_call = order_repo.update_order.await_args
    assert failed_call.kwargs["status"] == OrderStatus.FAILED
    assert failed_call.kwargs["error_message"] == "down"


async def test_cancel_queued_order(service, order_repo, notification_repo):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.QUEUED)

    order = await service.cancel_order("o1")

    assert order.status == OrderStatus.CANCELLED
    order_repo.update_order.assert_awaited_with("o1", status=OrderStatus.CANCELLED)
    saved = notification_repo.create_notification.await_args.args[0]
    assert saved.type == NotificationType.ORDER_CANCELLED


@pytest.mark.parametrize("status", [OrderStatus.COMPLETED, OrderStatus.FAILED, OrderStatus.CANCELLED])
async def test_cannot_cancel_finished_order(service, order_repo, status):
    order_repo.get_order_by_id.return_value = make_order(status=status)

    with pytest.raises(OrderCanNotBeCancelled):
        await service.cancel_order("o1")
    order_repo.update_order.assert_not_called()


async def test_missing_order(service, order_repo):
    order_repo.get_order_by_id.return_value = None

    with pytest.raises(OrderNotFound):
        await service.get_order_by_id("missing")


@pytest.mark.parametrize(
    "status",
    [OrderStatus.CREATED, OrderStatus.QUEUED, OrderStatus.PROCESSING, OrderStatus.COMPLETED],
)
async def test_manual_update_is_allowed_only_for_failed(service, order_repo, publish, status):
    order_repo.get_order_by_id.return_value = make_order(status=status)

    with pytest.raises(OrderCannotBeUpdated):
        await service.update_order("o1", OrderUpdate(status=OrderStatus.QUEUED))
    publish.assert_not_called()


async def test_failed_order_can_be_queued_again(service, order_repo, publish):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.FAILED)

    updated = await service.update_order("o1", OrderUpdate(status=OrderStatus.QUEUED))

    assert updated.status == OrderStatus.QUEUED
    publish.assert_awaited_once_with(service.rabbit, "o1", attempt=0)


async def test_requeue_marks_failed_when_queue_is_down(service, order_repo, publish):
    order_repo.get_order_by_id.return_value = make_order(status=OrderStatus.FAILED)
    publish.side_effect = RuntimeError("down")

    with pytest.raises(QueueUnavailable):
        await service.update_order("o1", OrderUpdate(status=OrderStatus.QUEUED))

    assert order_repo.update_order.await_args.kwargs["status"] == OrderStatus.FAILED


async def test_list_orders(service, order_repo):
    order_repo.get_list_of_orders.return_value = ([make_order()], 1)

    result = await service.get_all_orders(OrderListQuery())

    assert result.total == 1
    assert result.items[0].order_id == "o1"
