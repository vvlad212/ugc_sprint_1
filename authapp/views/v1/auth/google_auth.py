from http import HTTPStatus

from flask import url_for, request
from flask_restx import Namespace, Resource, ValidationError
from pydantic import BaseModel

from oauth import oauth
from services.auth_history_service import get_auth_history_service

from services.tokens_service import get_tokens_service
from services.user_service import get_user_service
from views.resp_models import internal_error_model
from views.v1.auth.auth import tokens_resp_model

auth_google_ns = Namespace(
    'GoogleAuth',
    description='Auth related operations',
    path='/google'
)


class GoogleCredentials(BaseModel):
    iss: str
    azp: str
    aud: str
    sub: str
    email: str
    email_verified: bool
    at_hash: str
    nonce: str
    name: str
    picture: str
    given_name: str
    family_name: str
    locale: str
    iat: int
    exp: int


@auth_google_ns.route('/login')
class Login(Resource):
    @auth_google_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', tokens_resp_model),
            HTTPStatus.UNAUTHORIZED: "Unauthorized",
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    "Internal error", internal_error_model
            ),
        }
    )
    def get(self):
        return oauth.google.authorize_redirect(url_for('GoogleAuth_authorize', _external=True))


@auth_google_ns.route('/authorize', doc=False)
class Authorize(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.user_service = get_user_service()
        self.token_service = get_tokens_service()
        self.auth_history_service = get_auth_history_service()

    def get(self):
        token = oauth.google.authorize_access_token()
        if token:
            try:
                user = GoogleCredentials(**token.get('userinfo'))
            except ValidationError:
                return {'error': 'Google response is not valid'}, HTTPStatus.BAD_REQUEST
            google_user = self.user_service.get_or_create_user_by_social(
                social_email=user.email,
                social_id=user.sub,
                social_name='google'
            )

            access_token = self.token_service.create_user_access_token(google_user)
            refresh_token = self.token_service.create_user_refresh_token(google_user)
            self.token_service.add_refresh_token_to_db(
                google_user,
                refresh_token,
                request.headers.get('User-Agent')
            )

            self.auth_history_service.add_auth_attempt_to_db(
                google_user,
                request.remote_addr,
                request.headers.get('User-Agent')
            )

            return {"access_token": access_token, "refresh_token": refresh_token}, HTTPStatus.OK

        return HTTPStatus.UNAUTHORIZED
