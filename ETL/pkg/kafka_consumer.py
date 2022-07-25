import logging
import backoff
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError
from core.req_handler import create_backoff_hdlr
from core import config

logger = logging.getLogger(__name__)
back_off_hdlr = create_backoff_hdlr(logger)

class KafkaConsumerClient:
    def __init__(self):
        self.topics = config.KAFKA_TOPICS
        self.auto_offset_reset = config.KAFKA_AUTO_OFFSET_RESET
        self.enable_auto_commit = config.KAFKA_ENABLE_AUTO_COMMIT
        self.bootstrap_servers = [f'{config.KAFKA_HOST}:{config.KAFKA_PORT}']
        self.group_id = config.KAFKA_GROUP_ID
        self.consumer_timeout_ms = config.KAFKA_CONSUMER_TIMEOUT_MS
        self.retry_backoff_ms = config.KAFKA_RETRY_BACKOFF_MS
        self.reconnect_backoff_ms = config.KAFKA_RECONNECT_BACKOFF_MS
        self.reconnect_backoff_max_ms = config.KAFKA_RECONNECT_BACKOFF_MAX_MS
        self.heartbeat_interval_ms = config.KAFKA_HEARTBEAT_INTERVAL_MS
        self.api_version_auto_timeout_ms = config.KAFKA_API_VERSION_AUTO_TIMEOUT_MS

    @backoff.on_exception(
        backoff.fibo,
        exception=(KafkaError, NoBrokersAvailable),
        max_time=60,
        max_tries = 100,
        on_backoff=back_off_hdlr,
    )
    def create_consumer(self):
        try:
            logger.info('Trying to connect to kafka')
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
            logger.info('Successful connection to kafka')
            return consumer
        except Exception as ex:
            logger.error(f'Error connecting to kafka')
            raise NoBrokersAvailable
