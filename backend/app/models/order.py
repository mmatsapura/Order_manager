from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class OrderStatus(str, Enum):
    CREATED = "Created"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    QUEUED = "Queued"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=1)


class Order(BaseModel):
    id: str| None = None
    order_id: str
    customer_name: str
    customer_email: EmailStr
    items: list[OrderItem]
    total_price: float
    status: OrderStatus = OrderStatus.CREATED
    retry_count: int = 0
    error_message: str | None = None
    processed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
