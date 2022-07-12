from authlib.integrations.flask_client import OAuth

from config import config
import logging
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api

from auth_jwt import init_jwt
from limiter import init_limiter
from oauth import init_oauth
from clicommands import init_clicommands
from db import init_db


from models.auth import AuthHistory
from models.roles import Role, UserRole
from models.tokens import UserRefreshToken
from models.user import User
from routes import register_routes
from jaeger_tracer import configure_tracer

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config.from_object(
    config.get(os.environ.get('ENV', 'default'))
)

jwt = JWTManager(app)

init_db(app)

init_jwt(app)

api = Api(
    app,
    prefix='/auth_api/v1',
    version='1.0',
    title='Auth Flask Api',
    description='A simple jwt token auth.',
    doc='/auth_api/doc/'
)
register_routes(api)

init_clicommands(app)

init_oauth(app)

init_limiter(app)

configure_tracer(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
