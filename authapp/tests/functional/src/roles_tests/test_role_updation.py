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
def admin_token(created_admin_user):
    tokens_service = get_tokens_service()
    yield tokens_service.create_user_access_token(created_admin_user)


def test_role_update(
    flask_app,
    headers,
    admin_token,
    roles
):
    """
    endpoint PUT /auth_api/v1/roles/ positive test
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.put(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "new_role_name": "shiny_role",
            "role_id": str(roles[0].id)
        }
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    roles = Role.query.all()
    assert len(roles) == 2, "wrong roles count after update"
    assert "shiny_role" in [
        role.name for role in roles
    ], "New name role not found in db"


def test_role_update_negative(
    flask_app,
    headers,
    admin_token,
):
    """
    endpoint PUT /auth_api/v1/roles/ negative test
    trying to update role that doesn't exist in db
    """
    headers['Authorization'] = f"Bearer {admin_token}"
    resp = flask_app.put(
        '/auth_api/v1/roles/',
        headers=headers,
        json={
            "new_role_name": "new_role_name",
            "role_id": "f76086a5-54d3-486c-b5fd-99e27e396861"
        }
    )

    assert resp.status_code == HTTPStatus.NOT_FOUND, "wrong status code"
    assert resp.json == {
        "message": f"Role:f76086a5-54d3-486c-b5fd-99e27e396861 is missing in db"
    }, "wrong error json resp for missing role"

    roles = Role.query.all()
    assert len(roles) == 2, "wrong roles count after update"
    assert "new_role_name" not in [
        role.name for role in roles
    ], "New name role not found in db"
