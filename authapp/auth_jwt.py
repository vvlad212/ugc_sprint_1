from os import environ
from flask import Flask
from flask_jwt_extended import JWTManager
import redis


jwt_redis_blocklist = redis.StrictRedis(
    host=environ.get('REDIS_HOST', 'localhost'),
    port=environ.get('REDIS_PORT', 6379),
    db=0,
    decode_responses=True
)


def init_jwt(app: Flask):
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None
