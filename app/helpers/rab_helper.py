import json
import logging
from aio_pika import connect, connect_robust, Message, IncomingMessage, DeliveryMode
from app.common.config import settings 
import asyncio

logger = logging.getLogger(__name__)

async def send_message(rabbitmq_channel, data: dict, queue_name: str = "question_queue") -> None:
    message_body = json.dumps(data).encode()
    message = Message(
        body=message_body,
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await rabbitmq_channel.default_exchange.publish(message, routing_key=queue_name)
    logger.info(f"Message sent to queue success '{queue_name}': {data}")


async def send_rabbitmq(channel, event: dict = {}, queue_name: str="" ) -> None:

    # Declaring exchange
    exchange = await channel.declare_exchange(
        name="exchange.document", type="direct", durable=True
    )

    # Declaring queue
    queue = await channel.declare_queue(name=queue_name, durable=True)

    # Binding queue to exchange
    await queue.bind(exchange, routing_key=queue_name)

    # Send message
    await exchange.publish(
        Message(json.dumps(event).encode("utf-8")), routing_key=queue_name
    )

    # await connection.close()
