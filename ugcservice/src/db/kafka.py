from typing import Optional

from aiokafka import AIOKafkaProducer

kafka: Optional[AIOKafkaProducer] = None


async def get_kafka() -> AIOKafkaProducer:
    return kafka
