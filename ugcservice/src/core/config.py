import os
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = "UGCStorageApi"

# Kafka settings
KAFKA_HOST = os.getenv('KAFKA_HOST', 'host.docker.internal')
KAFKA_PORT = os.getenv('KAFKA_PORT', '9092')

# Redis for limit req count
REDIS_LIMITER_HOST = os.getenv('REDIS_LIMITER_HOST', '127.0.0.1')
REDIS_LIMITER_PORT = os.getenv('REDIS_LIMITER_PORT', 6379)

ENV = os.getenv('ENV', 'dev')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
