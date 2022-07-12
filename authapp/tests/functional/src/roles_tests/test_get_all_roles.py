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
def roles():
    roles = [
        Role(name='user'),
        Role(name='manager'),
        Role(name='subscription'),
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
def tokens_service():
    return get_tokens_service()


def test_get_all_roles(
        flask_app,
        headers,
        tokens_service,
        created_admin_user
):
    """
    endpoint GET /auth_api/v1/roles/ positive test
    """
    headers['Authorization'] = f"Bearer {tokens_service.create_user_access_token(created_admin_user)}"
    resp = flask_app.get(
        '/auth_api/v1/roles/',
        headers=headers
    )

    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    roles = [{str(r.id): r.name} for r in Role.query.all()]
    assert resp.json['message'] == roles


def test_get_all_roles_negative(
        flask_app,
        headers,
        tokens_service,
        created_user
):
    """
    endpoint GET /auth_api/v1/roles/ negative test
    trying getting all roles wo admin role in access jwt
    """
    headers['Authorization'] = f"Bearer {tokens_service.create_user_access_token(created_user)}"
    resp = flask_app.post('/auth_api/v1/roles/', headers=headers)

    assert resp.status_code == HTTPStatus.FORBIDDEN, "wrong status code"
    assert resp.json == {'message': 'Admins only!'}, "wrong admin required error message"
