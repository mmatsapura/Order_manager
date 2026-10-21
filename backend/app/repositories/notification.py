from typing import List

from pymongo.asynchronous.database import AsyncDatabase

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: AsyncDatabase):
        self.notifications = db['notifications']

    @staticmethod
    def format_notification(order: dict) -> Notification:
        return Notification(id=str(order['_id']), order_id=order['order_id'], type=order['type'], message=order.get('message'), created_at=order['created_at'])

    async def create_notification(self, notif: Notification) -> Notification:
        payload = notif.model_dump(exclude={'id'})
        result = await self.notifications.insert_one(payload)
        notif.id = str(result.inserted_id)
        return notif

    async def get_notifications_by_order_id(self, order_id: str) -> List[Notification]:
        docs = await self.notifications.find({'order_id': order_id}).sort('created_at', 1).to_list(length=100)
        return [self.format_notification(doc) for doc in docs]
