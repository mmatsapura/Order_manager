import pytest
from pydantic import ValidationError

from app.schemas.order import OrderCreate, OrderListQuery
from app.schemas.user import UserCreate


def test_order_requires_items_and_email():
    with pytest.raises(ValidationError):
        OrderCreate(customer_name="Ann", customer_email="not-an-email", items=[])


def test_order_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        OrderCreate(
            customer_name="",
            customer_email="ann@example.com",
            items=[{"product_id": "p1", "quantity": 1}],
        )


def test_page_starts_at_one():
    with pytest.raises(ValidationError):
        OrderListQuery(page=0)


def test_password_length():
    with pytest.raises(ValidationError):
        UserCreate(email="ann@example.com", password="short")
    with pytest.raises(ValidationError):
        UserCreate(email="ann@example.com", password="x" * 33)
