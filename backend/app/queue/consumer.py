import asyncio
import logging

from app.queue.connection import RabbitMQ


logger = logging.getLogger(__name__)


async def consume(rabbitmq: RabbitMQ, handler):
    async with rabbitmq.queue.iterator() as queue:
        async for message in queue:
            async with message.process():
                try:
                    await handler(message.body)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Unhandled error while consuming a message")


async def consume_hello(rabbit: RabbitMQ) -> None:
    async with rabbit.queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("Received:", message.body.decode())
