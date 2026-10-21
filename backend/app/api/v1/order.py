from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import (
    OrderCanNotBeCancelled,
    OrderCannotBeUpdated,
    OrderNotFound,
    ProductNotFound,
)
from app.dependencies import (
    get_current_user,
    get_notification_repository,
    get_order_event_repository,
    get_order_repository,
    get_product_repository,
    get_rabbit_mq,
)
from app.models.order import OrderStatus
from app.models.user import User
from app.queue.connection import RabbitMQ
from app.repositories.notification import NotificationRepository
from app.repositories.order import OrderRepository
from app.repositories.order_event import OrderEventRepository
from app.repositories.product import ProductRepository
from app.schemas.notification import NotificationPublic
from app.schemas.order import (
    OrderCreate,
    OrderListQuery,
    OrderListResponse,
    OrderPublic,
    OrderUpdate,
)
from app.schemas.order_event import OrderEventPublic
from app.services.order import OrderService


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
async def get_orders(
        _current_user: User = Depends(get_current_user),
        order_repository: OrderRepository = Depends(get_order_repository),
        status: OrderStatus | None = None,
        email: str | None = None,
        order_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
):
    query = OrderListQuery(
        status=status,
        email=email,
        order_id=order_id,
        created_from=created_from,
        created_to=created_to,
        page=page,
        limit=limit,
    )
    service = OrderService(order_repository)
    return await service.get_all_orders(query)


@router.post("/{order_id}/cancel", response_model=OrderPublic)
async def cancel_order(order_id: str, _current_user: User = Depends(get_current_user),
                       order_repository: OrderRepository = Depends(get_order_repository),
                       notification_repository: NotificationRepository = Depends(get_notification_repository),
                       event_repository: OrderEventRepository = Depends(get_order_event_repository)):
    service = OrderService(
        order_repository,
        notification_repo=notification_repository,
        order_event_repo=event_repository,
    )
    try:
        return await service.cancel_order(order_id)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")
    except OrderCanNotBeCancelled:
        raise HTTPException(status_code=409, detail="Order cannot be cancelled")


@router.get("/{order_id}/notifications", response_model=list[NotificationPublic])
async def get_orders_notifications(order_id: str, _current_user: User = Depends(get_current_user),
                                   notification_repository: NotificationRepository = Depends(get_notification_repository),
                                   order_repository: OrderRepository = Depends(get_order_repository)):
    try:
        service = OrderService(order_repository)
        await service.get_order_by_id(order_id=order_id)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")
    return await notification_repository.get_notifications_by_order_id(order_id)


@router.get("/{order_id}/events", response_model=list[OrderEventPublic])
async def get_list_events(
        order_id: str,
        _current_user: User = Depends(get_current_user),
        event_repo: OrderEventRepository = Depends(get_order_event_repository),
        order_repository: OrderRepository = Depends(get_order_repository),
):
    service = OrderService(order_repo=order_repository, order_event_repo=event_repo)
    try:
        await service.get_order_by_id(order_id=order_id)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")
    events = await event_repo.get_events_by_order_id(order_id)
    return [OrderEventPublic.model_validate(event.model_dump()) for event in events]


@router.get("/{order_id}", response_model=OrderPublic)
async def get_order_by_order_id(
        order_id: str,
        _current_user: User = Depends(get_current_user),
        order_repository: OrderRepository = Depends(get_order_repository),
    ):
    service = OrderService(order_repository)
    try:
        return await service.get_order_by_id(order_id=order_id)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")


@router.post("", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    _current_user: User = Depends(get_current_user),
    order_repository: OrderRepository = Depends(get_order_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
    rabbitmq: RabbitMQ = Depends(get_rabbit_mq),
    event_repository: OrderEventRepository = Depends(get_order_event_repository),
    ):
    service = OrderService(
        order_repo=order_repository,
        product_repo=product_repository,
        rabbit=rabbitmq,
        order_event_repo=event_repository,
    )
    try:
        return await service.create_order(order=body)
    except ProductNotFound:
        raise HTTPException(status_code=400, detail="Unknown product")


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
        order_id: str,
        _current_user: User = Depends(get_current_user),
        order_repository: OrderRepository = Depends(get_order_repository),
):
    service = OrderService(order_repository)
    try:
        return await service.delete_order(order_id=order_id)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")


@router.patch("/{order_id}", response_model=OrderPublic)
async def update_order(order_id: str, body: OrderUpdate,
        _current_user: User = Depends(get_current_user),
                       order_repository: OrderRepository = Depends(get_order_repository),
                       rabbitmq: RabbitMQ = Depends(get_rabbit_mq),
                       event_repository: OrderEventRepository = Depends(get_order_event_repository)):
    service = OrderService(
        order_repo=order_repository,
        rabbit=rabbitmq,
        order_event_repo=event_repository,
    )
    try:
        return await service.update_order(order_id, body)
    except OrderNotFound:
        raise HTTPException(status_code=404, detail="Order not found")
    except OrderCannotBeUpdated:
        raise HTTPException(status_code=409, detail="Status transition not allowed")
