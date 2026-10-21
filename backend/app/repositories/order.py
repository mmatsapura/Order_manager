from typing import List
from datetime import datetime, timezone

from pymongo.asynchronous.database import AsyncDatabase

from app.models.order import Order
from app.schemas.order import OrderListQuery
from app.models.order import OrderStatus


class OrderRepository:
    def __init__(self, db: AsyncDatabase):
        self.orders = db['orders']

    @staticmethod
    def format_order(order: dict) -> Order:
        return Order(id=str(order['_id']), order_id=order['order_id'], customer_name=order['customer_name'], customer_email=order['customer_email'], items=order['items'], total_price=order['total_price'], status=order['status'], retry_count=order.get('retry_count', 0), error_message=order.get('error_message', None), processed_at=order.get('processed_at', None), created_at=order['created_at'], updated_at=order['updated_at'])

    async def get_order_by_id(self, order_id: str) -> Order | None:
        doc = await self.orders.find_one({'order_id': order_id})
        if doc:
            return self.format_order(doc)
        return None

    async def get_list_of_orders(self, query: OrderListQuery) -> tuple[(list[Order], int)]:
        filters = {}
        if query.status is not None:
            filters['status'] = query.status
        if query.order_id is not None:
            filters['order_id'] = query.order_id
        if query.email:
            filters['customer_email'] = {'$regex': query.email, '$options': 'i'}
        if query.created_from or query.created_to:
            rang = {}
            if query.created_from:
                rang['$gte'] = query.created_from
            if query.created_to:
                rang['$lte'] = query.created_to
            filters['created_at'] = rang
        total = await self.orders.count_documents(filters)
        skip = ((query.page - 1) * query.limit)
        docs = await self.orders.find(filters).sort('created_at', -1).skip(skip).limit(query.limit).to_list(length=query.limit)
        return ([self.format_order(order) for order in docs], total)

    async def create_order(self, order: Order) -> Order:
        payload = order.model_dump(exclude={'id'})
        result = await self.orders.insert_one(payload)
        order.id = str(result.inserted_id)
        return order

    async def delete_order(self, order_id: str):
        return await self.orders.delete_one({'order_id': order_id})

    async def update_order(self, order_id: str, **fields) -> None:
        fields['updated_at'] = datetime.now(timezone.utc)
        await self.orders.update_one({'order_id': order_id}, {'$set': fields})
        return

    def format_analytics(self, rows: list[dict]) -> dict:
        by_status = {s.value: 0 for s in OrderStatus}
        retry_attempts = 0
        avg_ms = None
        for row in rows:
            name = row.get('_id') or 'Unknown'
            if name in by_status:
                by_status[name] = row['count']
            retry_attempts += row.get('retries', 0)
            if name == OrderStatus.COMPLETED.value and row.get('avg_processing_ms') is not None:
                avg_ms = row['avg_processing_ms']
        total = sum(by_status.values())
        avg_seconds = round((avg_ms / 1000), 2) if avg_ms is not None else None
        return {'total_orders': total, 'processing_count': by_status[OrderStatus.PROCESSING.value], 'completed_count': by_status[OrderStatus.COMPLETED.value], 'failed_count': by_status[OrderStatus.FAILED.value], 'average_processing_seconds': avg_seconds, 'retry_attempts': retry_attempts, 'by_status': by_status}

    async def get_analytics(self) -> dict:
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}, 'retries': {'$sum': {'$ifNull': ['$retry_count', 0]}}, 'avg_processing_ms': {'$avg': {'$cond': [{'$ne': ['$processed_at', None]}, {'$subtract': ['$processed_at', '$created_at']}, None]}}}}]
        cursor = await self.orders.aggregate(pipeline)
        rows = await cursor.to_list(length=20)
        return self.format_analytics(rows)
