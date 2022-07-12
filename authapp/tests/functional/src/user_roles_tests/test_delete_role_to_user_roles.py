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
        Role(name='user'),
        Role(name='mega_users'),
        Role(name='admin'),
        Role(name='subscription'),

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
def admin_token(tokens_service, created_admin_user):
    return tokens_service.create_user_access_token(created_admin_user)


def test_delete_role_to_user_negative(
        flask_app,
        headers: dict,
        admin_token: str,
        created_user: User
):
    """
    endpoint POST /auth_api/v1/user_roles/ negative test
    Добавление не существующей в бд роли
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        f'/auth_api/v1/user_roles/?user_id={created_user.id}&role_id=9c258992-e942-4de4-80a2-2aaa9545b3c9',
        headers=headers,
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND, "wrong status code"
    assert resp.json == {'message': ['Role_id is missing in db.']}


def test_delete_role_to_user_negative2(
        flask_app,
        headers: dict,
        admin_token: str,
        created_user: User
):
    """
    endpoint POST /auth_api/v1/user_roles/ negative test
    Удаление не существующей у пользователя роли
    """
    role = Role.query.filter_by(name='subscription').first()
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        f'/auth_api/v1/user_roles/?user_id={created_user.id}&role_id={role.id}',
        headers=headers,
    )

    assert resp.status_code == HTTPStatus.NOT_FOUND, "wrong status code"
    assert resp.json == {'message': [f'User {created_user.id} does not have this role {role.id}.']}


def test_delete_role_to_user(
        flask_app,
        headers: dict,
        admin_token: str,
        created_user: User
):
    """
    endpoint DELETE /auth_api/v1/user_roles/ positive test
    """
    role = Role.query.filter_by(name='mega_users').first()
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        f'/auth_api/v1/user_roles/?user_id={created_user.id}&role_id={role.id}',
        headers=headers,
    )
    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    assert resp.json['message'] == f'The {role.id} role has been deleted to the user {created_user.id}'
    assert len(created_user.roles) == 1
    assert not role in created_user.roles
