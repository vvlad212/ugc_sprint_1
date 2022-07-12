import json
from hashlib import pbkdf2_hmac
from http import HTTPStatus
from db import db
from models.user import User


def test_not_valid_email(flask_app):
    response = flask_app.post('/auth_api/v1/registration/registration',
                              json={
                                  "login": "test",
                                  "password": "jksaga$f2D/.",
                              }
                              )
    assert response.status_code == HTTPStatus.BAD_REQUEST, "invalid HTTP status."
    assert json.loads(response.text) == {'errors': {'login': ['Not a valid email address.']}}


def test_not_valid_password(flask_app):
    response = flask_app.post('/auth_api/v1/registration/registration',
                              json={
                                  "login": "test@test.ru",
                                  "password": "jks",
                              }
                              )
    assert response.status_code == HTTPStatus.BAD_REQUEST, "invalid HTTP status."
    assert json.loads(response.text) == {'errors': {'password': ['Password has incorrect format.']}}


def test_wrong_json(flask_app):
    response = flask_app.post('/auth_api/v1/registration/registration',
                              json={
                                  "wrong_parameter1": "test@test.ru",
                                  "wrong_parameter2": "jks",
                              }
                              )
    assert response.status_code == HTTPStatus.BAD_REQUEST, "invalid HTTP status."
    assert json.loads(response.text) == {
        'errors':
            {
                "login": ["Missing data for required field."],
                "password": ["Missing data for required field."],
                "wrong_parameter1": ["Unknown field."],
                "wrong_parameter2": ["Unknown field."]
            }}, "invalid error text."


def test_add_user(flask_app):
    password = "P@ssw0rd/."
    login = "test_user_login@test.ru"
    response = flask_app.post('/auth_api/v1/registration/registration',
                              json={
                                  "login": login,
                                  "password": password,
                              }
                              )
    user_in_bd = User.query.filter_by(login=login).first()
    hash_password = pbkdf2_hmac(hash_name='sha256',
                                password=password.encode('utf-8'),
                                salt=bytes.fromhex(user_in_bd.salt),
                                iterations=1000)
    assert login == user_in_bd.login, "invalid login in BD."
    assert bytes.fromhex(user_in_bd.password) == hash_password, "invalid password hash."
    assert response.status_code == HTTPStatus.OK, "invalid HTTP status."
    assert json.loads(response.text) == {'msg': 'User has been added.'}, "bad application response."

    User.query.filter(User.login == "test_user_login@test.ru").delete()
    db.session.commit()


def test_wrong_add_user_already_exist(flask_app):
    flask_app.post('/auth_api/v1/registration/registration',
                   json={
                       "login": "test_user_login@test.ru",
                       "password": "P@ssw0rd/.",
                   }
                   )
    response = flask_app.post('/auth_api/v1/registration/registration',
                              json={
                                  "login": "test_user_login@test.ru",
                                  "password": "P@ssw0rd/.",
                              }
                              )
    assert response.status_code == HTTPStatus.BAD_REQUEST, "invalid response status."
    assert json.loads(response.text) == {'errors': {'login': ['This login already exists.']}}, "invalid errors text."
    User.query.filter(User.login == "test_user_login@test.ru").delete()
    db.session.commit()
