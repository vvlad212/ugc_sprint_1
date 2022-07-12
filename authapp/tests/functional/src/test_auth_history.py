import json
from http import HTTPStatus

import flask_jwt_extended
import pytest

from db import db
from models.auth import AuthHistory
from models.user import User

USER_TEST_AGENT = "werkzeug/2.1.2"
login = "squirrelmail@gmail.com"
password = "P4$$w0rd!"


@pytest.fixture(scope='module', autouse=True)
def auth_add(flask_app):
    flask_app.post('/auth_api/v1/registration/registration',
                   json={
                       "login": login,
                       "password": password,
                   }
                   )
    yield
    User.query.filter(User.login == login).delete()
    db.session.commit()


@pytest.fixture(scope='module', autouse=True)
def create_auth_history(flask_app):
    for i in range(1, 9):
        flask_app.post(
            '/auth_api/v1/auth/login', json={
                "login": login,
                "password": password
            }
        )
    yield
    User.query.filter(User.login == "squirrelmail@gmail.com").delete()
    db.session.commit()


def test_get_auth_history(flask_app):
    """
    endpoint /auth_api/v1/auth/history positive test
    """
    jwt_token = flask_app.post(
        '/auth_api/v1/auth/login', json={
            "login": login,
            "password": password
        }
    ).json.get('access_token')
    user_id = flask_jwt_extended.decode_token(jwt_token)['sub'].get('user_id')
    resp = flask_app.get('/auth_api/v1/auth/history', headers={'Authorization': f"Bearer {jwt_token}"})

    history = resp.json['message'].sort()
    bd_history = [[p.timestamp.strftime("%a, %d %b %Y %H:%M:%S GMT"), p.user_agent, p.user_ip] for p in
                  AuthHistory.query.filter_by(user_id=user_id).order_by(AuthHistory.timestamp).limit(10).all()].sort()
    assert resp.status_code == HTTPStatus.OK, "wrong status code"
    assert history == bd_history, "wrong response data"
