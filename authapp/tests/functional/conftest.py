from dataclasses import dataclass
from logging import getLogger

from flask_migrate import upgrade
import pytest
from multidict import CIMultiDictProxy

from app import app
from db import db
from auth_jwt import jwt_redis_blocklist

logger = getLogger(__name__)


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session', autouse=True)
def flask_app():
    app.config.from_object('config.TestConfig')
    with app.app_context():
        upgrade(directory='migrations')
        yield app.test_client()
        db.session.close()
        db.drop_all()
        db.engine.execute("DROP TABLE alembic_version")
        jwt_redis_blocklist.flushall()
