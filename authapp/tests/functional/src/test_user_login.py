import json
from http import HTTPStatus
from typing import Tuple

from flask_jwt_extended import decode_token
import pytest

from db import db
from models.user import User
from models.auth import AuthHistory
from models.tokens import UserRefreshToken
from models.roles import Role, UserRole
from services.user_service import get_user_service

USER_LOGIN_TEST = "squirrelmail@gmail.com"


@pytest.fixture(scope='module')
def headers():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture(scope='module')
def user_service():
    return get_user_service()


@pytest.fixture(scope='module', autouse=True)
def create(user_service):
    user_service.create_user(
        login=USER_LOGIN_TEST,
        password="P4$$w0rd!"
    )
    AuthHistory
    yield "create_test_user"
    User.query.filter(User.login == USER_LOGIN_TEST).delete()
    db.session.commit()


@pytest.fixture(scope='module')
def test_user():
    return User.query.filter_by(login=USER_LOGIN_TEST).first()


@pytest.fixture(scope='module')
def test_user_roles(test_user):
    role_1 = Role(name='test_role_1')
    role_2 = Role(name='test_role_2')
    db.session.add_all((role_1, role_2,))
    db.session.commit()

    u_role_1 = UserRole(user_id=test_user.id, role_id=role_1.id)
    u_role_2 = UserRole(user_id=test_user.id, role_id=role_2.id)
    db.session.bulk_save_objects((u_role_1, u_role_2,))
    db.session.commit()
    yield role_1, role_2
    Role.query.filter(Role.id.in_((role_1.id, role_1.id))).delete()
    db.session.commit()


def test_user_login(
    flask_app,
    headers: dict,
    test_user: User,
    test_user_roles: Tuple[Role]
):
    """
    endpoint /auth_api/v1/auth/login positive test
    """
    resp = flask_app.post(
        '/auth_api/v1/auth/login',
        data=json.dumps({
            "login": "squirrelmail@gmail.com",
            "password": "P4$$w0rd!"
        }),
        headers=headers
    )

    # result checking
    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    # check access token claims
    decoded_token = decode_token(resp.json['access_token'])
    assert decoded_token.get('exp') != None,\
        "wrong expiration time in access token"

    assert sorted(decoded_token['sub']['user_roles']) == [
        role.name for role in test_user_roles
    ],\
        "wrong roles in assess token claims"

    assert decoded_token['sub']['user_id'] == str(test_user.id),\
        "wrong user_id in assess token claims"

    # checking that the refresh token has been written to db
    ref_token = (
        UserRefreshToken.query
        .filter_by(
            user_id=test_user.id
        )
        .first()
    )
    assert ref_token != None, "ref token not found in db"
    assert ref_token.token == resp.json['refresh_token'],\
        "wrong ref token has been recorded"

    # checking that auth history has been written to db
    auth_stories = (
        AuthHistory.query
        .filter_by(
            user_id=test_user.id
        )
        .all()
    )
    assert len(auth_stories) == 1, "wrong auth stories count"
    assert auth_stories[0].user_id == test_user.id,\
        "wrong user_id in auth story"
    assert auth_stories[0].user_agent == "werkzeug/2.1.2",\
        "wrong user_agent in auth story"
    assert auth_stories[0].user_ip == "127.0.0.1",\
        "wrong user_ip in auth story"


def test_user_login_negative_1(flask_app, headers):
    """
    endpoint /auth_api/v1/auth/login negative test
    with bad credentials
    """
    # wrong login
    resp = flask_app.post(
        '/auth_api/v1/auth/login',
        data=json.dumps({
            "login": "sssquirrelmail@gmail.com",
            "password": "P4$$w0rd!"
        }),
        headers=headers
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED, "wrong status code"
    assert resp.json == {'error': 'Bad credentials'}

    # wrong password
    resp = flask_app.post(
        '/auth_api/v1/auth/login',
        data=json.dumps({
            "login": "squirrelmail@gmail.com",
            "password": "PPP4$$w0rd!"
        }),
        headers=headers
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED, "wrong status code"
    assert resp.json == {'error': 'Bad credentials'}


def test_user_login_negative_2(flask_app, headers):
    """
    endpoint /auth_api/v1/auth/login negative test
    with validation errors:
        login is not email and short password
        missing parameters and wrong parameters 
    """
    # login is not email and short password
    resp = flask_app.post(
        '/auth_api/v1/auth/login',
        data=json.dumps({
            "login": "squirrelmailgmail.com",
            "password": "P4"
        }),
        headers=headers
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST, "wrong status code"
    assert resp.json == {
        'errors': {
            'login': ['Not a valid email address'],
            'password': ['Shorter than minimum length 6.']
        }
    }, "wrong validation error body in email error and short pwd"

    # missing parameters and wrong parameters
    resp = flask_app.post(
        '/auth_api/v1/auth/login',
        data=json.dumps({
            "log": "squirrelmail@gmail.com",
            "pwd": "P!!!E@%DSFHsdh4"
        }),
        headers=headers
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST, "wrong status code"
    assert resp.json == {
        'errors': {
            'password': ['Missing data for required field.'],
            'login': ['Missing data for required field.'],
            'log': ['Unknown field.'],
            'pwd': ['Unknown field.']
        }
    }, "wrong validation error body in missing params test"
