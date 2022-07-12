from http import HTTPStatus

import pytest

from db import db
from models.user import User
from models.tokens import UserRefreshToken
from services.user_service import get_user_service
from services.tokens_service import get_tokens_service

USER_TEST_AGENT = "werkzeug/2.1.2"


@pytest.fixture(scope='module')
def created_user():
    test_user_login = "squirrelmail@gmail.com"
    user_service = get_user_service()
    user_service.create_user(
        login=test_user_login,
        password="P4$$w0rd!"
    )
    yield User.query.filter_by(login=test_user_login).first()
    User.query.filter(User.login == test_user_login).delete()
    db.session.commit()


@pytest.fixture(scope='module')
def old_refresh_token(created_user):
    tokens_service = get_tokens_service()
    ref_token = tokens_service.create_user_refresh_token(created_user)
    tokens_service.add_refresh_token_to_db(
        created_user,
        ref_token,
        USER_TEST_AGENT
    )
    return ref_token


def test_user_login(
    flask_app,
    created_user: User,
    old_refresh_token: str
):
    """
    endpoint /auth_api/v1/auth/revoke_refresh positive test
    """
    resp = flask_app.delete(
        '/auth_api/v1/auth/revoke_refresh',
        headers={'Authorization': f"Bearer {old_refresh_token}"}
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    assert resp.json == {'msg': 'Refresh token was successfully revoked'},\
        "wrong resp body while trying to revoke refresh token"

    # checking that refresh token is no longer exists in db
    user_token = UserRefreshToken.query.filter_by(
        user_id=created_user.id,
        user_agent=USER_TEST_AGENT,
        token=old_refresh_token
    ).first()
    assert user_token == None, "old refresh token still can be found in db"

    # checking that refresh token is blacklisted
    resp = flask_app.delete(
        '/auth_api/v1/auth/revoke_refresh',
        headers={'Authorization': f"Bearer {old_refresh_token}"}
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED, "wrong status code"
    assert resp.json == {"msg": "Token has been revoked"},\
        "wrong resp body while trying to revoke already revoked refresh token"
