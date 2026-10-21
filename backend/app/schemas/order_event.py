from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderEventPublic(BaseModel):
    order_id: str
    from_status: (OrderStatus | None) = None
    to_status: OrderStatus
    created_at: datetime
