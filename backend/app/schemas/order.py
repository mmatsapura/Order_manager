from datetime import datetime

from pydantic import BaseModel, Field, EmailStr

from app.models.order import OrderStatus, OrderItem


class OrderItemInput(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=50)
    customer_email: EmailStr
    items: list[OrderItemInput] = Field(min_length=1)


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderPublic(BaseModel):
    order_id: str
    customer_name: str
    customer_email: EmailStr
    items: list[OrderItem]
    total_price: float
    status: OrderStatus
    retry_count: int
    created_at: datetime
    updated_at: datetime


class OrderListQuery(BaseModel):
    email: (str | None) = None
    status: (OrderStatus | None) = None
    order_id: (str | None) = None
    created_from: (datetime | None) = None
    created_to: (datetime | None) = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class OrderListResponse(BaseModel):
    items: list[OrderPublic]
    total: int
    page: int
    limit: int
