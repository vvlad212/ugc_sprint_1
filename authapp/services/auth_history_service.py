from functools import lru_cache
from http import HTTPStatus
import logging
from typing import List
from uuid import UUID

from flask_restx import abort
from opentelemetry import trace

from jaeger_tracer import jaeger_trace
from db import db
from models.user import User
from models.auth import AuthHistory

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class AuthHistoryService:

    @jaeger_trace(
        {
            'span_name': "auth attempt saving in db",
        },
        tracer
    )
    def add_auth_attempt_to_db(
            self,
            user: User,
            user_ip: str,
            user_agent: str
    ) -> None:
        logger.info(f'Adding login attempt to db for user: {user.id}.')
        try:
            new_auth = AuthHistory(
                user=user,
                user_ip=user_ip,
                user_agent=user_agent,
            )
            db.session.add(new_auth)
            db.session.commit()
        except Exception:
            logging.exception("Error while trying to save auth attempt to db.")
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_auth(self, user_id: UUID) -> List:
        """Получение истории успешных попыток входа."""
        try:
            logger.info(f'Getting authorization history for a user: {user_id}.')
            return [[p.timestamp, p.user_agent, p.user_ip] for p in
                    AuthHistory.query.filter_by(user_id=user_id).order_by(AuthHistory.timestamp).limit(10).all()]
        except:
            logging.exception("Error getting authorization history for a user: {user_id}.")
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)


@lru_cache()
def get_auth_history_service():
    return AuthHistoryService()
