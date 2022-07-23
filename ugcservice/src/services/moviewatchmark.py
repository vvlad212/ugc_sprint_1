import datetime
from functools import lru_cache
import logging
from typing import Union
from uuid import UUID
from fastapi import Depends
from pkg.storage.kafka_storage import get_kafka_storage_service
from pkg.storage.storage import ABSStorage

logger = logging.getLogger(__name__)

AUTH_VIEWS_TOPIC = "auth_views_labels"
UNAUTH_VIEWS_TOPIC = "unauth_views_labels"


class MovieWatchMarkService:
    def __init__(self, storage: ABSStorage):
        self.storage = storage

    async def save_watchmark(
        self,
        film_id: Union[str, UUID],
        user_id: Union[str, UUID, None],
        timestamp: datetime.time
    ) -> bool:
        logger.info(
            "User:{} is trying to send film:{} watchmark timestamp{} into Kafka storage.".format(
                "unauthorized user" if not user_id else user_id,
                film_id,
                timestamp
            )
        )
        
        if user_id:
            topic = AUTH_VIEWS_TOPIC
            key = f'{film_id}_{user_id}'
        else:
            topic = UNAUTH_VIEWS_TOPIC
            key = str(film_id)+'_00000000-0000-0000-0000-000000000000'

        if await self.storage.send_to_ugc_storage(
            topic=topic,
            value=timestamp.isoformat(),
            key=key
        ):
            logger.info("Watchmark has been saved.")
            return True
        logger.info("Watchmark hasn't been saved.")
        return False


@lru_cache()
def get_watchmark_service(
    storage: ABSStorage = Depends(get_kafka_storage_service)
) -> MovieWatchMarkService:
    return MovieWatchMarkService(storage=storage)
