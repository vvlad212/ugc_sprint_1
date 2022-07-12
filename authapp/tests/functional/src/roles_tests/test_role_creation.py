from http import HTTPStatus
import pytest

from db import db
from models.user import User
from models.roles import Role
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
        Role(name='admin')
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
    user.roles = [roles[0]]
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


def test_role_creation(
    flask_app,
    headers,
    tokens_service,
    created_admin_user
):
    """
    endpoint POST /auth_api/v1/roles/ positive test
    """
    headers['Authorization'] = f"Bearer {tokens_service.create_user_access_token(created_admin_user)}"
    resp = flask_app.post(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "new_role_name": "new_role",
        }
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    roles = Role.query.all()
    assert "new_role" in [
        role.name for role in roles
    ], "New role not found in db"


def test_role_creation_negative_1(
    flask_app,
    headers,
    tokens_service,
    created_user
):
    """
    endpoint POST /auth_api/v1/roles/ negative test
    trying to create role wo admin role in access jwt
    """
    headers['Authorization'] = f"Bearer {tokens_service.create_user_access_token(created_user)}"
    resp = flask_app.post(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "new_role_name": "new_user_role",
        }
    )

    assert resp.status_code == HTTPStatus.FORBIDDEN, "wrong status code"
    assert resp.json == {'message': 'Admins only!'},\
        "wrong admin required error message"

    roles = Role.query.all()
    assert "new_user_role" not in [  # not
        role.name for role in roles
    ], "new_user_role found in db"


def test_role_creation_negative_2(
    flask_app,
    headers,
    tokens_service,
    created_admin_user,
    roles
):
    """
    endpoint POST /auth_api/v1/roles/ positive test
    trying to create role that already exists
    """
    headers['Authorization'] = f"Bearer {tokens_service.create_user_access_token(created_admin_user)}"
    resp = flask_app.post(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "new_role_name": roles[0].name,
        }
    )

    assert resp.status_code == HTTPStatus.CONFLICT, "wrong status code"
    assert resp.json == {'message': 'Role already exist.'},\
        "wrong role already exist error message"

    assert [role.name for role in Role.query.all()].count(roles[0].name) == 1,\
        "Wrong roles count"
