from http import HTTPStatus
import pytest

from db import db
from models.user import User
from models.roles import Role
from services.tokens_service import get_tokens_service
from services.user_service import get_user_service


@pytest.fixture(scope='module')
def headers():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture(scope='module')
def created_admin_user():
    test_admin_user_login = "admin_user@gmail.com"
    user_service = get_user_service()
    user_service.create_user(
        login=test_admin_user_login,
        password="P4$$w0rd!"
    )
    admin_user = User.query.filter_by(login=test_admin_user_login).first()
    roles = [
        Role(name='user'),
        Role(name='admin')
    ]
    db.session.add_all(roles)
    admin_user.roles = roles
    db.session.commit()
    yield admin_user
    db.session.delete(admin_user)
    Role.query.delete()
    db.session.commit()


@pytest.fixture(scope='module')
def admin_token(created_admin_user):
    tokens_service = get_tokens_service()
    yield tokens_service.create_user_access_token(created_admin_user)


def test_role_deletion(
    flask_app,
    headers,
    admin_token,
):
    """
    endpoint DELETE /auth_api/v1/roles/ positive test
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "role_name": "user",
        }
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    # checking that user role has been removed
    roles = Role.query.all()
    assert "user" not in [
        role.name for role in roles
    ], "Role that has been deleted was found in db"


def test_role_deletion_negative_1(
    flask_app,
    headers,
    admin_token,
):
    """
    endpoint DELETE /auth_api/v1/roles/ negative test
    trying to delete admin role
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "role_name": "admin",
        }
    )

    assert resp.status_code == HTTPStatus.FORBIDDEN, "wrong status code"

    assert resp.json == {'message': 'Deleting admin role is forbidden.'},\
        "wrong deleting admin role error message"

    # checking that role hasn't been removed
    roles = Role.query.all()
    assert "admin" in [
        role.name for role in roles
    ], "Role that has been deleted was found in db"


def test_role_deletion_negative_2(
    flask_app,
    headers,
    admin_token,
):
    """
    endpoint DELETE /auth_api/v1/roles/ negative test
    trying to delete missing role
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.delete(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "role_name": "missing_role",
        }
    )

    assert resp.status_code == HTTPStatus.NO_CONTENT,\
        "wrong status code for missing role"
