import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ES_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ES_PORT', 9200))

ENV = os.getenv('ENV', 'test')

AUTH_SERVICE= os.getenv('AUTH_SERVICE', 'http://127.0.0.1:8000/auth_api/v1/auth/check_roles')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
