import asyncio
import logging
from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.config import settings
from app.models.notification import Notification, NotificationType
from app.models.order import OrderStatus
from app.models.order_event import OrderEvent
from app.queue.connection import RabbitMQ
from app.queue.producer import publish_order
from app.repositories.notification import NotificationRepository
from app.repositories.order import OrderRepository
from app.repositories.order_event import OrderEventRepository
from app.schemas.queue import QueueMessage


logger = logging.getLogger(__name__)


class QueueProcessingService:
    def __init__(
        self,
        order_repo: OrderRepository,
        notif_service: NotificationRepository,
        rabbit: RabbitMQ,
        order_event_repo: OrderEventRepository,
    ):
        self.order_repo = order_repo
        self.notif_service = notif_service
        self.rabbit = rabbit
        self.order_event_repo = order_event_repo

    async def create_notification(
        self,
        order_id: str,
        ntype: NotificationType,
        message: str | None,
    ) -> Notification:
        await self.notif_service.create_notification(
            Notification(order_id=order_id, type=ntype, message=message)
        )

    async def log_status(
        self,
        order_id: str,
        to_status: OrderStatus,
        from_status: OrderStatus | None = None,
    ) -> None:
        await self.order_event_repo.create_event(
            OrderEvent(order_id=order_id, from_status=from_status, to_status=to_status)
        )

    async def handle(self, body: bytes) -> None:
        try:
            msg = QueueMessage.model_validate_json(body)
        except ValidationError:
            logger.exception("Invalid queue message: %s", body)
            return
        order = await self.order_repo.get_order_by_id(msg.order_id)
        if order is None or order.status == OrderStatus.CANCELLED:
            logger.info("Order %s cancelled during processing, skip complete", msg.order_id)
            return
        try:
            logger.info("New order start processing %s", order.order_id)
            logger.info(f"Msg {msg} retrieving from queue")
            previous = order.status
            await self.order_repo.update_order(msg.order_id, status=OrderStatus.PROCESSING)
            await self.log_status(msg.order_id, OrderStatus.PROCESSING, from_status=previous)
            await asyncio.sleep(settings.processing_delay_seconds)
            order = await self.order_repo.get_order_by_id(msg.order_id)
            if order is None or order.status == OrderStatus.CANCELLED:
                return
            await self.order_repo.update_order(
                msg.order_id,
                status=OrderStatus.COMPLETED,
                processed_at=datetime.now(timezone.utc),
                error_message=None,
            )
            await self.log_status(
                msg.order_id,
                OrderStatus.COMPLETED,
                from_status=OrderStatus.PROCESSING,
            )
            await self.create_notification(
                order_id=msg.order_id,
                ntype=NotificationType.ORDER_COMPLETED,
                message=str(msg),
            )
            logger.info("New order completed %s", order.order_id)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await self.fail_or_retry(msg, exc)

    async def fail_or_retry(self, msg: QueueMessage, error: Exception) -> None:
        order = await self.order_repo.get_order_by_id(msg.order_id)
        if order is None or order.status == OrderStatus.CANCELLED:
            return
        retry_count = msg.attempt + 1
        error_message = str(error)
        logger.exception(
            "Order %s failed on attempt %s: %s",
            msg.order_id,
            retry_count,
            error_message,
        )
        previous = order.status
        if retry_count < settings.max_retries:
            await self.order_repo.update_order(
                msg.order_id,
                status=OrderStatus.QUEUED,
                retry_count=retry_count,
                error_message=error_message,
            )
            await self.log_status(msg.order_id, OrderStatus.QUEUED, from_status=previous)
            await publish_order(self.rabbit, msg.order_id, attempt=retry_count)
            return
        await self.order_repo.update_order(
            msg.order_id,
            status=OrderStatus.FAILED,
            retry_count=retry_count,
            error_message=error_message,
        )
        await self.log_status(msg.order_id, OrderStatus.FAILED, from_status=previous)
        await self.create_notification(
            order_id=msg.order_id,
            ntype=NotificationType.ORDER_FAILED,
            message=error_message,
        )
