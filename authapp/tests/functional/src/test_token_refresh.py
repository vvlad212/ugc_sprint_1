from http import HTTPStatus

from flask_jwt_extended import decode_token
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
    endpoint /auth_api/v1/auth/refresh positive test
    """
    resp = flask_app.post(
        '/auth_api/v1/auth/refresh',
        headers={'Authorization': f"Bearer {old_refresh_token}"}
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    new_ref_token = resp.json['refresh_token']
    access_decoded_token = decode_token(resp.json['access_token'])
    refresh_decoded_token = decode_token(new_ref_token)
    assert access_decoded_token['sub']['user_id'] == str(created_user.id),\
        "wrong user_id in assess token claims"
    assert refresh_decoded_token['sub']['user_id'] == str(created_user.id),\
        "wrong user_id in refresh token claims"

    # checking that new token has been written to db
    user_token = UserRefreshToken.query.filter_by(
        user_id=created_user.id,
        user_agent=USER_TEST_AGENT,
        token=new_ref_token
    ).first()
    assert user_token != None, "new refresh token is missing in db"

    # checking, that old token is no longer aviliable
    resp = flask_app.post(
        '/auth_api/v1/auth/refresh',
        headers={'Authorization': f"Bearer {old_refresh_token}"}
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED, "wrong status code"

    assert resp.json == {'message': 'This refresh token is no longer available'},\
        "wrong error message for olf refresh token"

    # cheching, that tokens can be refreshed by new ref. token
    resp = flask_app.post(
        '/auth_api/v1/auth/refresh',
        headers={'Authorization': f"Bearer {new_ref_token}"}
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    access_decoded_token = decode_token(resp.json['access_token'])
    refresh_decoded_token = decode_token(resp.json['refresh_token'])
    assert access_decoded_token['sub']['user_id'] == str(created_user.id),\
        "wrong user_id in assess token claims"
    assert refresh_decoded_token['sub']['user_id'] == str(created_user.id),\
        "wrong user_id in refresh token claims"
