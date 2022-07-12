from http import HTTPStatus
import logging
import os
from functools import lru_cache
from hashlib import pbkdf2_hmac
import secrets
import string
from typing import Optional

from flask_restx import abort
from opentelemetry import trace

from db import db
from models.user import SocialAccount, User
from marshmallow import ValidationError
from jaeger_tracer import jaeger_trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
iterations: int = 1000


class UserService:
    def __init__(self):
        self.db = db

    def create_user(
            self,
            login: str,
            password: str
    ) -> Optional[User]:
        logger.info(
            f"Trying to create user:{login}."
        )
        salt = os.urandom(32)
        hash_password = pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode('utf-8'),
            salt=salt,
            iterations=iterations
        )
        try:
            user = User(
                login=login,
                password=hash_password.hex(),
                salt=salt.hex(),
                iterations=iterations
            )
            db.session.add(user)
            db.session.commit()
        except Exception as er:
            logger.error(f'Error when adding user, {er}')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        logger.info(
            f'User:{user.id} with login:{login} has been created successfully.')
        return user

    @jaeger_trace({'span_name': 'verifying check'}, tracer)
    def is_user_verified(
            self,
            user_login: str,
            password: str
    ) -> Optional[User]:
        """
        User credentials checking.
        """
        logger.info(f"Verifying user: {user_login}")
        try:
            user = User.query.filter_by(login=user_login).first()
        except Exception:
            logger.exception(
                f"Error while trying to get user {user_login} from db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        if user is None or not self.verify_user_password(user, password):
            return None
        logger.info(f"User {user_login} has been verified.")
        return user

    @jaeger_trace({'span_name': 'password verifying'}, tracer)
    def verify_user_password(self, user: User, password: str):
        hashed_password = pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode('utf-8'),
            salt=bytes.fromhex(user.salt),
            iterations=user.iterations
        )
        return bytes.fromhex(user.password) == hashed_password

    def change_user_password(self,
                             login: str,
                             new_password: str,
                             old_password: str):
        logger.info(f"Trying to change password for user: {login}")
        if new_password == old_password:
            raise ValidationError(
                'The password must be different from the current one.'
            )
        user = self.is_user_verified(user_login=login, password=old_password)
        salt = os.urandom(32)
        hash_password = pbkdf2_hmac(
            hash_name='sha256',
            password=new_password.encode('utf-8'),
            salt=salt,
            iterations=iterations
        )
        try:
            User.query.filter_by(id=user.id).update(
                {
                    "password": hash_password.hex(),
                    "salt": salt.hex(),
                    "iterations": iterations
                }
            )
            db.session.commit()
            logger.info(f"Password has been changed for user: {login}")
        except Exception:
            logger.exception(
                f"Error while trying to change password for user {login} from db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def change_login(
            self,
            old_login: str,
            new_login: str,
            password: str
    ):
        logger.info(f"Trying to change login for user: {old_login}")
        user = self.is_user_verified(user_login=old_login, password=password)
        try:
            User.query.filter_by(id=user.id).update({"login": new_login})
            db.session.commit()
            logger.info(f"Login has been changed for user: {old_login}")
        except Exception:
            logger.exception(
                f"Error while trying to change login for user {old_login} from db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_or_create_user_by_social(
            self,
            social_id: str,
            social_name: str,
            social_email: str = None,
    ) -> User:
        logger.info(
            f"Trying to get user:{social_id} by {social_name} social acc"
        )
        try:
            user_soc_acc = (
                SocialAccount.query
                .filter_by(
                    social_id=social_id,
                    social_name=social_name
                ).first()
            )
        except Exception:
            logger.exception(
                f"Error while trying to get {social_name} user:{social_id} from db."
            )
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

        if user_soc_acc:
            return user_soc_acc.user
        else:
            logger.info(
                f"Trying to get user with {social_email} login."
            )
            try:
                user = User.query.filter_by(login=social_email).first()
            except Exception:
                logger.exception(
                    f"Error while trying to get user:{social_email} from db."
                )
                abort(HTTPStatus.INTERNAL_SERVER_ERROR)
            if not user:
                user = self.create_user(
                    social_email,
                    ''.join(
                        secrets.choice(string.ascii_letters + string.digits)
                        for i in range(10)
                    )
                )
            logger.info(
                f"Trying to create soc acc for user:{user.id}."
            )
            try:
                user_soc_acc = SocialAccount(
                    user_id=user.id,
                    social_id=social_id,
                    social_name=social_name
                )
                db.session.add(user_soc_acc)
                db.session.commit()
            except Exception:
                logger.exception(f'Error while trying to create user soc acc.')
                abort(HTTPStatus.INTERNAL_SERVER_ERROR)

        return user


@lru_cache()
def get_user_service():
    return UserService()
