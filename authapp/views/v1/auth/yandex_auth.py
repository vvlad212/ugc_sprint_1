from http import HTTPStatus

import requests
from flask import request, url_for
from flask_restx import Namespace, Resource

from oauth import oauth
from services.user_service import get_user_service
from services.auth_history_service import get_auth_history_service
from services.tokens_service import get_tokens_service
from views.resp_models import internal_error_model
from .auth import tokens_resp_model

yandex_auth_ns = Namespace(
    'Yandex_auth',
    description='Auth with Yandex OAuth 2.0',
    path='/auth/yandex'
)


@yandex_auth_ns.route('/login')
class StartYandexAuth(Resource):
    @yandex_auth_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', tokens_resp_model),
            HTTPStatus.UNAUTHORIZED: "Unauthorized",
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                "Internal error", internal_error_model
            ),
        }
    )
    def get(self):
        redirect_uri = url_for(
            'Yandex_auth_authorize_yandex_auth', _external=True
        )
        return oauth.yandex.authorize_redirect(redirect_uri)


@yandex_auth_ns.route('/authorize', doc=False)
class AuthorizeYandexAuth(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()
        self.token_service = get_tokens_service()
        self.auth_history_service = get_auth_history_service()

    def get(self):
        auth_code = request.args.get('code', False)
        if auth_code:
            # geting yandex tokens
            result_json = requests.post(
                oauth.yandex.access_token_url,
                {
                    'grant_type': 'authorization_code',
                    'code': request.args.get('code'),
                    'client_id': oauth.yandex.client_id,
                    'client_secret': oauth.yandex.client_secret
                }
            ).json()

            # getting yandex user info
            result_json = requests.get(
                f"{oauth.yandex.api_base_url}/info",
                params={'format': 'json', 'with_openid_identity': 'yes'},
                headers={
                    "Authorization": f"OAuth {result_json.get('access_token')}"
                }
            ).json()

            # get user by socials
            yandex_user = self.user_service.get_or_create_user_by_social(
                social_id=result_json.get('id'),
                social_name='yandex',
                social_email=result_json.get('default_email')
            )

            access_token = self.token_service.create_user_access_token(
                yandex_user
            )
            refresh_token = self.token_service.create_user_refresh_token(
                yandex_user
            )
            self.token_service.add_refresh_token_to_db(
                yandex_user,
                refresh_token,
                request.headers.get('User-Agent')
            )

            self.auth_history_service.add_auth_attempt_to_db(
                yandex_user,
                request.remote_addr,
                request.headers.get('User-Agent')
            )

            return {
                "access_token": access_token, "refresh_token": refresh_token
            }, HTTPStatus.OK

        return HTTPStatus.UNAUTHORIZED
