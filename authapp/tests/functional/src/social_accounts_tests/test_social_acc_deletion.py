from http import HTTPStatus
from flask import Flask

import pytest
from services.tokens_service import get_tokens_service

from db import db
from models.user import User, SocialAccount
from services.user_service import get_user_service


@pytest.fixture(scope='module')
def headers():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture(scope='module')
def test_user() -> User:
    test_user_login = "squirrelmail@gmail.com"
    user_service = get_user_service()
    user = user_service.create_user(
        login=test_user_login,
        password="P4$$w0rd!"
    )
    db.session.add(
        SocialAccount(
            user=user,
            social_id="2582103205",
            social_name="google",
        )
    )
    db.session.commit()
    yield user
    User.query.filter(User.login == test_user_login).delete()
    db.session.commit()


@pytest.fixture(scope='module')
def soc_acc_to_be_deleted(test_user) -> SocialAccount:
    soc_acc = SocialAccount(
        user=test_user,
        social_id="1545134295",
        social_name="yandex",
    )
    db.session.add(soc_acc)
    db.session.commit()
    return soc_acc


@pytest.fixture(scope='module')
def access_token(test_user) -> str:
    tokens_service = get_tokens_service()
    return tokens_service.create_user_access_token(
        test_user
    )


def test_delete_user_soc_acc(
    flask_app: Flask,
    headers: dict,
    access_token: str,
    soc_acc_to_be_deleted: SocialAccount,
    test_user: User
):
    """
    endpoint DELETE /auth_api/v1/soc/ positive test
    """
    headers['Authorization'] = f"Bearer {access_token}"
    resp = flask_app.delete(
        "/auth_api/v1/soc/",
        headers=headers,
        json={
            "soc_network_id": soc_acc_to_be_deleted.id,
        }
    )
    assert resp.status_code == HTTPStatus.OK, "wrong status code"

    assert len(test_user.social_accounts) == 1,\
        "wrong social networks accounts count"
    assert soc_acc_to_be_deleted not in test_user.social_accounts,\
        "deleted role has been found in users roles"


def test_delete_user_soc_acc_negative_1(
    flask_app: Flask,
    headers: dict,
    access_token: str,
):
    """
    endpoint DELETE /auth_api/v1/soc/ negative test
    wrong deletion id
    """
    headers['Authorization'] = f"Bearer {access_token}"
    resp = flask_app.delete(
        "/auth_api/v1/soc/",
        headers=headers,
        json={
            "soc_network_id": "c1cf95ee-9825-462c-9897-746ed992b784",
        }
    )
    assert resp.status_code == HTTPStatus.NO_CONTENT, "wrong status code"
