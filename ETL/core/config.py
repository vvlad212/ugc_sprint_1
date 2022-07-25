import os
from logging import config as logging_config
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

# Kafka settings
KAFKA_HOST = os.getenv('KAFKA_HOST', 'host.docker.internal')
KAFKA_PORT = os.getenv('KAFKA_PORT', '9092')

KAFKA_TOPICS = os.getenv('KAFKA_TOPICS', ['auth_views_labels', 'unauth_views_labels'])
KAFKA_AUTO_OFFSET_RESET = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
KAFKA_ENABLE_AUTO_COMMIT = os.getenv('KAFKA_ENABLE_AUTO_COMMIT', False)
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'upload_to_clickhouse')
KAFKA_CONSUMER_TIMEOUT_MS = os.getenv('KAFKA_CONSUMER_TIMEOUT_MS', 5000)
KAFKA_RETRY_BACKOFF_MS = os.getenv('KAFKA_RETRY_BACKOFF_MS', 3000)
KAFKA_RECONNECT_BACKOFF_MS = os.getenv('KAFKA_RECONNECT_BACKOFF_MS', 5000)
KAFKA_RECONNECT_BACKOFF_MAX_MS = os.getenv('KAFKA_RECONNECT_BACKOFF_MAX_MS', 10000)
KAFKA_HEARTBEAT_INTERVAL_MS = os.getenv('KAFKA_HEARTBEAT_INTERVAL_MS', 5000)
KAFKA_API_VERSION_AUTO_TIMEOUT_MS = os.getenv('KAFKA_API_VERSION_AUTO_TIMEOUT_MS', 5000)
KAFKA_BATCH_SIZE = int(os.getenv('KAFKA_BATCH_SIZE', 1000))

# clickhouse settings
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'clickhouse-node1')
CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'default')
CLICKHOUSE_TABLE = os.getenv('CLICKHOUSE_TABLE', 'views')
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'app')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', 'qwe123')
