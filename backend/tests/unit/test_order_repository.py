from datetime import datetime, timezone

from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.order import OrderRepository
from app.schemas.order import OrderListQuery
from tests.fakes import FakeDB


def order(order_id, status=OrderStatus.CREATED, email="ann@example.com", created_at=None):
    return Order(
        order_id=order_id,
        customer_name="Ann",
        customer_email=email,
        items=[OrderItem(product_id="p1", name="Tea", price=10, quantity=1)],
        total_price=10,
        status=status,
        created_at=created_at or datetime.now(timezone.utc),
    )


async def test_create_get_update_delete():
    repo = OrderRepository(FakeDB())
    created = await repo.create_order(order("o1"))

    loaded = await repo.get_order_by_id("o1")
    assert loaded.id == created.id
    assert loaded.status == OrderStatus.CREATED

    await repo.update_order("o1", status=OrderStatus.QUEUED, retry_count=2)
    loaded = await repo.get_order_by_id("o1")
    assert loaded.status == OrderStatus.QUEUED
    assert loaded.retry_count == 2

    await repo.delete_order("o1")
    assert await repo.get_order_by_id("o1") is None


async def test_list_filters_and_pages():
    repo = OrderRepository(FakeDB())
    await repo.create_order(order("old", status=OrderStatus.FAILED, email="old@example.com", created_at=datetime(2020, 1, 1, tzinfo=timezone.utc)))
    await repo.create_order(order("new", status=OrderStatus.COMPLETED, email="Ann@example.com", created_at=datetime(2024, 6, 1, tzinfo=timezone.utc)))

    items, total = await repo.get_list_of_orders(OrderListQuery(status=OrderStatus.COMPLETED, email="ann"))
    assert total == 1
    assert items[0].order_id == "new"

    items, total = await repo.get_list_of_orders(
        OrderListQuery(created_from=datetime(2023, 1, 1, tzinfo=timezone.utc), page=1, limit=1)
    )
    assert total == 1
    assert items[0].order_id == "new"


def test_format_analytics_ignores_unknown_status():
    repo = OrderRepository({"orders": None})
    result = repo.format_analytics([
        {"_id": "Completed", "count": 2, "retries": 1, "avg_processing_ms": 2500},
        {"_id": "Failed", "count": 1, "retries": 3, "avg_processing_ms": None},
        {"_id": None, "count": 9, "retries": 4},
    ])

    assert result["total_orders"] == 3
    assert result["completed_count"] == 2
    assert result["failed_count"] == 1
    assert result["average_processing_seconds"] == 2.5
    assert result["retry_attempts"] == 8
    assert result["by_status"]["Completed"] == 2
