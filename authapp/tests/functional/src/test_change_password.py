from hashlib import pbkdf2_hmac
from http import HTTPStatus

import pytest

from db import db
from models.user import User

login = "squirrelmail@gmail.com"
old_password = "P4$$w0rd!"
new_password = "P4$$w0rdnew"


@pytest.fixture(scope='module', autouse=True)
def add_user(flask_app):
    flask_app.post('/auth_api/v1/registration/registration',
                   json={"login": login, "password": old_password})
    yield
    User.query.filter(User.login == login).delete()
    db.session.commit()


@pytest.fixture(scope='module')
def jwt_token(flask_app):
    resp = flask_app.post(
        '/auth_api/v1/auth/login', json={
            "login": login,
            "password": old_password
        }
    )

    yield resp.json.get('access_token')


def test_new_password_already_exist(flask_app, jwt_token):
    """
        endpoint /auth_api/v1/change_credentials/password negative test
    """
    response = flask_app.post('/auth_api/v1/change_credentials/password',
                              json={"password_old": old_password,
                                    "password_new": old_password,
                                    "login": login},
                              headers={'Authorization': f"Bearer {jwt_token}"})

    assert response.status_code == HTTPStatus.BAD_REQUEST, "invalid response status."
    assert response.json == {'errors': ['The password must be different from the current one.']}, "invalid errors text."


def test_new_password(flask_app, jwt_token):
    """
       endpoint /auth_api/v1/change_credentials/password positive test
    """
    response = flask_app.post('/auth_api/v1/change_credentials/password',
                              json={"password_old": old_password,
                                    "password_new": new_password,
                                    "login": login},
                              headers={'Authorization': f"Bearer {jwt_token}"})

    assert response.status_code == HTTPStatus.OK, "invalid response status."
    assert response.json == {'message': 'The password has been changed.'}, "invalid errors text."

    user_in_bd = User.query.filter_by(login=login).first()
    hash_password = pbkdf2_hmac(hash_name='sha256',
                                password=new_password.encode('utf-8'),
                                salt=bytes.fromhex(user_in_bd.salt),
                                iterations=1000)
    assert bytes.fromhex(user_in_bd.password) == hash_password, "invalid password hash."
