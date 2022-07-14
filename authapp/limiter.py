import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=config.get(os.environ.get('ENV', 'default')).REQUESTS_LIMITER,
    storage_uri=f'redis://{os.environ.get("REDIS_HOST","127.0.0.1")}:{os.environ.get("REDIS_PORT", 6379)}')
    # storage_uri=f'redis://127.0.0.1:6379')


def init_limiter(app: Flask):
    limiter.init_app(app)
