import logging
import os

import backoff
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError
from pkg.req_handler import create_backoff_hdlr

logger = logging.getLogger(__name__)

BACKOFF_MAX_TIME = 60  # sec
back_off_hdlr = create_backoff_hdlr(logger)


class KafkaConsumerClient:
    def __init__(self):
        self.topics = ['auth_views_labels']#, 'unauth_views_labels']
        self.auto_offset_reset = 'earliest'
        self.enable_auto_commit = False
        self.bootstrap_servers = [f"{os.getenv('KAFKA_HOST', 'host.docker.internal')}:29092"]
        self.group_id = 'upload_to_clickhouse'
        self.consumer_timeout_ms = 5000
        self.retry_backoff_ms = 3000
        self.reconnect_backoff_ms = 5000
        self.reconnect_backoff_max_ms = 10000
        self.heartbeat_interval_ms = 5000
        self.api_version_auto_timeout_ms = 5000

    @backoff.on_exception(
        backoff.fibo,
        exception=(KafkaError, NoBrokersAvailable),
        max_time=BACKOFF_MAX_TIME,
        on_backoff=back_off_hdlr,
    )
    def create_consumer(self):
        try:
            consumer = KafkaConsumer(
                *self.topics,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                consumer_timeout_ms=self.consumer_timeout_ms,
                retry_backoff_ms=self.retry_backoff_ms,
                reconnect_backoff_ms=self.reconnect_backoff_ms,
                reconnect_backoff_max_ms=self.reconnect_backoff_max_ms,
                heartbeat_interval_ms=self.heartbeat_interval_ms,
                api_version_auto_timeout_ms=self.api_version_auto_timeout_ms
            )
            return consumer
        except Exception as ex:
            logger.error(f'Failed connection to brokers {ex}')
            raise NoBrokersAvailable
