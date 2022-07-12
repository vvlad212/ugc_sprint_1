from http import HTTPStatus

import pytest

from db import db
from models.user import User
from services.user_service import get_user_service
from services.tokens_service import get_tokens_service


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
def access_token_to_revoke(created_user):
    tokens_service = get_tokens_service()
    return tokens_service.create_user_access_token(created_user)


def test_access_token_revoke(
    flask_app,
    access_token_to_revoke: str
):
    """
    endpoint /auth_api/v1/auth/revoke_access positive test
    """
    resp = flask_app.delete(
        '/auth_api/v1/auth/revoke_access',
        headers={'Authorization': f"Bearer {access_token_to_revoke}"}
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    assert resp.json == {"msg": "Access token was successfully revoked"},\
        "wrong resp body while trying to revoke access token"

    # checking, that old access token is no longer avaliable
    resp = flask_app.delete(
        '/auth_api/v1/auth/revoke_access',
        headers={'Authorization': f"Bearer {access_token_to_revoke}"}
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED, "wrong status code"
    assert resp.json == {"msg": "Token has been revoked"},\
        "wrong resp body while trying to revoke already revoked access token"
