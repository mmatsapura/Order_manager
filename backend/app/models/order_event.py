from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderEvent(BaseModel):
    id: (str | None) = None
    order_id: str
    from_status: (OrderStatus | None) = None
    to_status: OrderStatus
    created_at: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
