from hashlib import pbkdf2_hmac
from http import HTTPStatus

import pytest

from db import db
from models.user import User

old_login = "squirrelmail@gmail.com"
new_login = "Newsquirrelmail@gmail.com"
password = "P4$$w0rd!"



@pytest.fixture(scope='module', autouse=True)
def add_user(flask_app):
    flask_app.post('/auth_api/v1/registration/registration',
                   json={"login": old_login, "password": password})
    yield
    User.query.filter(User.login == old_login).delete()
    db.session.commit()


@pytest.fixture(scope='module')
def jwt_token(flask_app):
    resp = flask_app.post(
        '/auth_api/v1/auth/login', json={
            "login": old_login,
            "password": password
        }
    )
    yield resp.json.get('access_token')


def test_change_login(flask_app, jwt_token):
    """
       endpoint /auth_api/v1/change_credentials/login positive test
    """
    response = flask_app.post('/auth_api/v1/change_credentials/login',
                              json={"password": password,
                                    "login_new": new_login,
                                    "login_old": old_login},
                              headers={'Authorization': f"Bearer {jwt_token}"})

    assert response.status_code == HTTPStatus.OK, "invalid response status."
    assert response.json == {'message': 'The login has been changed.'}, "invalid errors text."
    user_in_bd = User.query.filter_by(login=new_login).first()
    assert user_in_bd.login == new_login, "invalid login value."
