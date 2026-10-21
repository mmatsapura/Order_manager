from typing import List

from pymongo.asynchronous.database import AsyncDatabase

from app.models.order_event import OrderEvent


class OrderEventRepository:
    def __init__(self, db: AsyncDatabase):
        self.events = db['order_events']

    @staticmethod
    def format_event(order: dict) -> OrderEvent:
        return OrderEvent(id=str(order['_id']), order_id=order['order_id'], from_status=order.get('from_status'), to_status=order.get('to_status'), created_at=order.get('created_at'))

    async def create_event(self, order_event: OrderEvent) -> OrderEvent:
        payload = order_event.model_dump(exclude={'id'})
        result = await self.events.insert_one(payload)
        order_event.id = str(result.inserted_id)
        return order_event

    async def get_events_by_order_id(self, order_id: str) -> List[OrderEvent]:
        docs = await self.events.find({'order_id': order_id}).sort('created_at', 1).to_list(length=200)
        return [self.format_event(order_event) for order_event in docs]
