from datetime import datetime

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationPublic(BaseModel):
    order_id: str
    type: NotificationType
    message: (str | None)
    created_at: (datetime | None)
