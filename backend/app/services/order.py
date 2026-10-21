import uuid

from app.core.exceptions import ProductNotFound, OrderNotFound, QueueUnavailable, OrderCanNotBeCancelled, OrderCannotBeUpdated
from app.models.order import Order, OrderItem, OrderStatus
from app.models.order_event import OrderEvent
from app.repositories.product import ProductRepository
from app.repositories.order import OrderRepository
from app.repositories.order_event import OrderEventRepository
from app.models.notification import Notification, NotificationType
from app.repositories.notification import NotificationRepository
from app.schemas.order import OrderCreate, OrderUpdate, OrderListResponse, OrderListQuery, OrderPublic
from app.queue.producer import publish_order
from app.schemas.analytics import AnalyticsPublic


CANCELLABLE = (OrderStatus.CREATED, OrderStatus.QUEUED, OrderStatus.PROCESSING)
MANUAL_TRANSITION = {OrderStatus.FAILED: {OrderStatus.QUEUED}}


class OrderService:
    def __init__(self, order_repo: OrderRepository, notification_repo: NotificationRepository = None, product_repo: ProductRepository = None, rabbit=None, order_event_repo: OrderEventRepository = None) -> None:
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.rabbit = rabbit
        self.notification_repo = notification_repo
        self.order_event_repo = order_event_repo

    async def log_status(self, order_id: str, to_status: OrderStatus, from_status: (OrderStatus | None) = None) -> None:
        if self.order_event_repo is None:
            return
        await self.order_event_repo.create_event(OrderEvent(order_id=order_id, from_status=from_status, to_status=to_status))
        return

    async def cancel_order(self, order_id: str) -> Order:
        order = await self.order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFound()
        if order.status not in CANCELLABLE:
            raise OrderCanNotBeCancelled(order.status)
        if self.notification_repo is None:
            raise RuntimeError("notification_repo is required to cancel an order")
        previous = order.status
        await self.order_repo.update_order(order_id, status=OrderStatus.CANCELLED)
        await self.log_status(order_id, OrderStatus.CANCELLED, from_status=previous)
        await self.notification_repo.create_notification(Notification(order_id=order_id, type=NotificationType.ORDER_CANCELLED, message=f'ORDER {order_id} CANCELLED'))
        order.status = OrderStatus.CANCELLED
        return order

    async def create_order(self, order: OrderCreate) -> Order:
        if self.product_repo is None or self.rabbit is None:
            raise RuntimeError("product_repo and rabbit are required to create an order")
        items = []
        for line in order.items:
            product = await self.product_repo.get_product_by_id(line.product_id)
            if product is None:
                raise ProductNotFound()
            items.append(OrderItem(product_id=product.id, name=product.name, price=product.price, quantity=line.quantity))
        total = sum(((item.price * item.quantity) for item in items))
        new_order = Order(order_id=str(uuid.uuid4()), customer_name=order.customer_name, customer_email=order.customer_email, items=items, total_price=total, status=OrderStatus.CREATED)
        await self.order_repo.create_order(new_order)
        await self.log_status(new_order.order_id, OrderStatus.CREATED)
        try:
            await publish_order(self.rabbit, new_order.order_id, attempt=0)
        except Exception as exc:
            await self.order_repo.update_order(
                new_order.order_id,
                status=OrderStatus.FAILED,
                error_message=str(exc),
            )
            await self.log_status(new_order.order_id, OrderStatus.FAILED, from_status=OrderStatus.CREATED)
            raise QueueUnavailable() from exc
        await self.order_repo.update_order(new_order.order_id, status=OrderStatus.QUEUED)
        await self.log_status(new_order.order_id, OrderStatus.QUEUED, from_status=OrderStatus.CREATED)
        new_order.status = OrderStatus.QUEUED
        return new_order

    async def get_order_by_id(self, order_id: str) -> Order:
        order = await self.order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFound()
        return order

    async def get_all_orders(self, query: OrderListQuery) -> OrderListResponse:
        items, total = await self.order_repo.get_list_of_orders(query)
        return OrderListResponse(items=[OrderPublic.model_validate(item.model_dump()) for item in items], total=total, page=query.page, limit=query.limit)

    async def delete_order(self, order_id: str) -> None:
        order = await self.order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFound()
        await self.order_repo.delete_order(order_id)
        return

    async def update_order(self, order_id, body: OrderUpdate) -> Order:
        order = await self.order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFound()
        allowed = MANUAL_TRANSITION.get(order.status, set())
        if body.status not in allowed:
            raise OrderCannotBeUpdated()
        if body.status == OrderStatus.QUEUED and self.rabbit is None:
            raise QueueUnavailable()
        previous = order.status
        await self.order_repo.update_order(order_id, status=body.status)
        await self.log_status(order_id, body.status, from_status=previous)
        if body.status == OrderStatus.QUEUED:
            try:
                await publish_order(self.rabbit, order.order_id, attempt=0)
            except Exception as exc:
                await self.order_repo.update_order(
                    order_id,
                    status=OrderStatus.FAILED,
                    error_message=str(exc),
                )
                await self.log_status(order_id, OrderStatus.FAILED, from_status=body.status)
                raise QueueUnavailable() from exc
        order.status = body.status
        return order

    async def get_analytics(self) -> AnalyticsPublic:
        payload = await self.order_repo.get_analytics()
        return AnalyticsPublic.model_validate(payload)
