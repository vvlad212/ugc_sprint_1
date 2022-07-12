from functools import lru_cache
from http import HTTPStatus
import logging
from typing import Optional
from uuid import UUID

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restx import abort
from opentelemetry import trace

from db import db
from auth_jwt import jwt_redis_blocklist
from models.tokens import UserRefreshToken
from models.user import User
from jaeger_tracer import jaeger_trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class TokensService:

    @jaeger_trace(
        {
            'span_name': "access token creation",
        },
        tracer
    )
    def create_user_access_token(self, user: User) -> str:
        logger.info(f'Trying to create access token for user: {user.id}')
        try:
            access_token = create_access_token(
                identity={
                    'user_id': user.id,
                    'user_roles': [role.name for role in user.roles]
                }
            )
        except Exception:
            logging.exception(
                f"Error while trying to create access token for user {user.id}"
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return access_token

    @jaeger_trace(
        {
            'span_name': "refresh token creation",
        },
        tracer
    )
    def create_user_refresh_token(self, user: User) -> str:
        logger.info(f'Trying to create refresh token for user: {user.id}')
        try:
            refresh_token = create_refresh_token(
                identity={'user_id': user.id}
            )
        except Exception:
            logging.exception(
                f"Error while trying to create refresh token for user {user.id}"
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return refresh_token

    @jaeger_trace(
        {
            'span_name': "refresh token saving in db",
        },
        tracer
    )
    def add_refresh_token_to_db(
        self,
        user: User,
        token: str,
        user_agent: str
    ) -> None:
        logger.info(f'Adding refresh token to db for user: {user.id}.')
        try:
            user_token = UserRefreshToken.query.filter_by(
                user_id=user.id,
                user_agent=user_agent
            ).first()
            if not user_token:
                user_token = UserRefreshToken(
                    user=user,
                    token=token,
                    user_agent=user_agent,
                )
            else:
                user_token.token = token
            db.session.add(user_token)
            db.session.commit()
        except Exception:
            logging.exception(
                "Error while trying to save refresh token to db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_user_from_token_claims(self, claims: dict) -> Optional[User]:
        logger.info(f"Trying to get user from token claims {claims}")
        user_id = claims.get('user_id')
        if not user_id:
            abort(HTTPStatus.BAD_REQUEST, "missing user_id in token claims.")
        try:
            user = User.query.filter_by(id=user_id).first()
        except Exception:
            logger.exception(
                f"Error while trying to get user {user_id} from db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return user

    def check_refresh_token_relevance(
        self,
        user_id: UUID,
        user_agent: str,
        token: str
    ) -> Optional[UserRefreshToken]:
        logger.info(
            f"Checking refresh token relevance for user_id: {user_id}."
        )
        try:
            user_token = UserRefreshToken.query.filter_by(
                user_id=user_id,
                user_agent=user_agent,
                token=token
            ).first()
        except Exception:
            logger.exception(
                f"Error while trying to check refresh token for user: {user_id}"
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return user_token

    def revoke_access_token(self, jwt: dict) -> None:
        logger.info(
            f"Trying to revoke access token: {jwt}."
        )
        try:
            jwt_redis_blocklist.set(jwt["jti"], "", ex=jwt['exp'] - jwt['iat'])
        except Exception:
            logger.exception(
                f"Error adding access token into blocklist"
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def revoke_refresh_token(self, jwt: dict, user_agent: str, jwt_raw: str) -> None:
        logger.info(
            f"Trying to revoke refresh token: {jwt}."
        )
        user_id = jwt.get('sub', {}).get('user_id')
        if not user_id:
            abort(HTTPStatus.BAD_REQUEST, "missing user_id in token claims.")

        try:
            jwt_redis_blocklist.set(jwt["jti"], "", ex=jwt['exp'] - jwt['iat'])
        except Exception:
            logger.exception(
                f"Error adding refresh into blocklist"
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            UserRefreshToken.query.filter_by(
                user_id=user_id,
                user_agent=user_agent,
                token=jwt_raw
            ).delete()
            db.session.commit()
        except Exception:
            logger.exception(
                f"Error removing refresh token from db"
            )


@lru_cache()
def get_tokens_service():

    return TokensService()
