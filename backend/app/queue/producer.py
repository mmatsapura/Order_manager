import aio_pika

from app.queue.connection import RabbitMQ, QUEUE_NAME
from app.schemas.queue import QueueMessage


async def publish_order(rabbitmq: RabbitMQ, order_id: str, attempt: int =0) -> None:
    payload = QueueMessage(order_id=order_id, attempt=attempt)
    message = aio_pika.Message(body=payload.model_dump_json().encode(),
                               delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                               content_type='application/json')
    await rabbitmq.channel.default_exchange.publish(message, routing_key=QUEUE_NAME)


async def publish_hello(rabbitmq: RabbitMQ):
    message = aio_pika.Message(
        body=b"Hello World",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    await rabbitmq.channel.default_exchange.publish(
        message, routing_key=QUEUE_NAME,
    )
    print("Sent: Hello World")
