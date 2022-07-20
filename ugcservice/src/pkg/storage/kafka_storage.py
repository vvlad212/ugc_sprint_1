import logging
from functools import lru_cache
from aiokafka import AIOKafkaProducer

from fastapi import Depends
from pkg.storage.storage import ABSStorage
from db.kafka import get_kafka


logger = logging.getLogger(__name__)


class KafkaService(ABSStorage):
    def __init__(self, kafka: AIOKafkaProducer) -> None:
        self.kafka = kafka

    async def send_to_ugc_storage(
        self,
        topic: str,
        value: str,
        key: str
    ) -> bool:
        try:
            await self.kafka.send_and_wait(
                topic=topic,
                value=str.encode(value),
                key=str.encode(key)
            )
        except Exception:
            logger.exception("Failed to send message to Kafka.")
            return False
        return True


@lru_cache()
def get_kafka_storage_service(
        kafka: KafkaService = Depends(get_kafka),
) -> KafkaService:
    return KafkaService(kafka)
