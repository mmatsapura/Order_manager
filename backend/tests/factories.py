from app.models.order import Order, OrderItem, OrderStatus


def make_order(**overrides) -> Order:
    data = dict(
        order_id="o1",
        customer_name="Ann",
        customer_email="ann@example.com",
        items=[OrderItem(product_id="p1", name="Tea", price=10, quantity=2)],
        total_price=20,
        status=OrderStatus.CREATED,
    )
    data.update(overrides)
    return Order(**data)
