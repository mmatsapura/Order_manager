import asyncio
import logging

from app.core.config import settings
from app.db.db import MongoDB
from app.queue.connection import RabbitMQ
from app.queue.consumer import consume
from app.repositories.notification import NotificationRepository
from app.repositories.order import OrderRepository
from app.repositories.order_event import OrderEventRepository
from app.services.queue_processing import QueueProcessingService


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    mongo = MongoDB(settings.mongodb_url, settings.mongodb_database)
    rabbit = RabbitMQ(settings.rabbitmq_url)
    await mongo.connect()
    await rabbit.connect()
    service = QueueProcessingService(
        OrderRepository(mongo.db),
        NotificationRepository(mongo.db),
        rabbit,
        OrderEventRepository(mongo.db),
    )
    try:
        await consume(rabbit, service.handle)
    except asyncio.CancelledError:
        logging.info("Worker stopped")
    finally:
        await rabbit.close()
        await mongo.close()


if __name__ == "__main__":
    asyncio.run(main())
