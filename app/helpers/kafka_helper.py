import json
import logging

from confluent_kafka import Producer

from app.common.config import settings
from app.helpers.decorator import run_async

logger = logging.getLogger("API-Service")
producer_conf = {
    "bootstrap.servers": settings.KAFKA_INTERNAL,
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanism": "SCRAM-SHA-256",
    # "sasl.mechanism": "PLAIN",
    "acks": "all",
    "sasl.username": settings.KAFKA_USERNAME,
    "sasl.password": settings.KAFKA_PASSWORD,
    "message.max.bytes": 5242880
}


@run_async
def pussNotification(idcard, status, channel):
    try:
        logger.info(
            f"Pushing {idcard} of channel:{channel} to {settings.KAFKA_NOTI_TOPIC} "
        )
        data = {"channel": channel, "data": {"idCardNo": idcard, "status": status}}
        producer = Producer(producer_conf)
        producer.produce(settings.KAFKA_NOTI_TOPIC, key=idcard, value=json.dumps(data))
        producer.flush()
        logger.info(
            msg=f"Pushed {idcard} of channel:{channel} to {settings.KAFKA_NOTI_TOPIC} "
        )
    except Exception as e:
        logger.error(
            f"Error when pushing message to {settings.KAFKA_NOTI_TOPIC} with exception:{e.__str__()}"
        )
        raise Exception(f"Error when push message to {settings.KAFKA_NOTI_TOPIC}")


async def pushMessage(topic, key, mess, header=None):
    try:
        logger.info(f"Pushing {key} to {topic} ")
        logger.info(f"value message {json.dumps(mess)}")
        producer = Producer(producer_conf)
        producer.produce(topic=topic, key=key, headers=header, value=json.dumps(mess))
        producer.flush()
    except Exception as e:
        logger.error(
            f"Error when pushing message to {topic} with exception:{e.__str__()}"
        )
        raise Exception(f"Error when push message to {topic}")
