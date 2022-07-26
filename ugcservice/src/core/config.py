from logging import config as logging_config

from pydantic import BaseSettings
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Config(BaseSettings):
    """Base config."""
    KAFKA_HOST: str = "host.docker.internal"
    KAFKA_PORT: str = "9092"

    REDIS_LIMITER_HOST: str = "127.0.0.1"
    REDIS_LIMITER_PORT: str = "6379"

    ENV: str = "dev"

    class Config:
        env_prefix = ""
        case_sensitive = False
