import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from app.core.config import settings


QUEUE_NAME = 'orders'


class RabbitMQ:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection = None
        self._channel = None
        self.queue = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=1)
        self.queue = await self._channel.declare_queue(QUEUE_NAME, durable=True)
        return

    async def close(self) -> None:
        if self._connection is not None:
            if not (self._connection.is_closed):
                await self._connection.close()
        self._connection = None
        self._channel = None
        self.queue = None
        return

    @property
    def channel(self) -> AbstractChannel:
        if self._channel is None:
            raise RuntimeError('RabitMQ is not connected')
        return self._channel

    async def ping(self) -> None:
        if self._connection is not None:
            if self._connection.is_closed:
                raise RuntimeError('RabbitMQ is not connected')
        if self._channel is None:
            raise RuntimeError('RabbitMQ channel is closed')
        if self._channel.is_closed:
            raise RuntimeError('RabbitMQ channel is closed')
