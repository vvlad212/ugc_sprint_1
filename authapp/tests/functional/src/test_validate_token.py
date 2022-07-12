from datetime import datetime
from http import HTTPStatus

import pytest

from db import db
from models.roles import Role
from models.user import User
from services.tokens_service import get_tokens_service
from services.user_service import get_user_service

USER_TEST_AGENT = "werkzeug/2.1.2"


@pytest.fixture(scope='module')
def headers():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture(scope='module')
def roles():
    roles = [
        Role(name='subscription'),
        Role(name='admin'),
    ]
    db.session.add_all(roles)
    db.session.commit()
    yield roles
    Role.query.delete()
    db.session.commit()


@pytest.fixture(scope='module')
def created_user(roles):
    test_user_login = "squirrelmail@gmail.com"
    user_service = get_user_service()
    user_service.create_user(
        login=test_user_login,
        password="P4$$w0rd!"
    )
    user = User.query.filter_by(login=test_user_login).first()
    user.roles = roles[:2]
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


@pytest.fixture(scope='module')
def created_admin_user(roles):
    test_admin_user_login = "admin_user@gmail.com"
    user_service = get_user_service()
    user_service.create_user(
        login=test_admin_user_login,
        password="P4$$w0rd!"
    )
    admin_user = User.query.filter_by(login=test_admin_user_login).first()
    admin_user.roles = roles
    db.session.commit()
    yield admin_user
    db.session.delete(admin_user)
    db.session.commit()


@pytest.fixture(scope='module')
def tokens_service():
    return get_tokens_service()


@pytest.fixture(scope='module')
def user_token(tokens_service, created_user):
    return tokens_service.create_user_access_token(created_user)


@pytest.fixture(scope='module')
def admin_token(tokens_service, created_admin_user):
    return tokens_service.create_user_access_token(created_admin_user)


def test_validate_token_and_resp_roles(
        flask_app,
        headers: dict,
        user_token: str,
        created_user: User
):
    """
    endpoint GET /auth_api/v1/auth/check_roles positive test
    """
    headers['Authorization'] = f"Bearer {user_token}"
    resp = flask_app.get(
        f'/auth_api/v1/auth/check_roles',
        headers=headers,
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    assert len(resp.json.get('user_roles')) == 2, "wrong roles count"
    assert 'subscription' in resp.json['user_roles']
    assert 'admin' in resp.json['user_roles']


def test_validate_token_and_resp_roles_negative(
        flask_app,
        headers: dict,
):
    """
    endpoint GET /auth_api/v1/auth/check_roles negative test
    """
    headers['Authorization'] = f"Bearer "
    resp = flask_app.get(
        f'/auth_api/v1/auth/check_roles',
        headers=headers,
    )

    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, "wrong status code"
    assert resp.json.get('user_roles') is None
