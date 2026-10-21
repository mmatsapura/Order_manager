from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    ORDER_COMPLETED = 'Order Completed'
    ORDER_FAILED = 'Order Failed'
    ORDER_CANCELLED = 'Order Cancelled'


class Notification(BaseModel):
    id: (str | None) = None
    order_id: str
    type: NotificationType
    message: (str | None) = None
    created_at: (datetime | None) = Field(default_factory=lambda : datetime.now(timezone.utc))
