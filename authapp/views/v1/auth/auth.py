import os
from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from flask_restx import Namespace, Resource, abort, fields
from marshmallow import (
    Schema,
    fields as ma_fields,
    ValidationError,
    validate
)
from opentelemetry import trace

from limiter import limiter
from services.user_service import get_user_service
from services.tokens_service import get_tokens_service
from services.auth_history_service import get_auth_history_service
from views.resp_models import (
    internal_error_model,
    unauth_error_resp_model,
)
from views.req_models import token_in_headers
from jaeger_tracer import jaeger_trace

tracer = trace.get_tracer(__name__)

auth_ns = Namespace(
    'Auth',
    description='Auth related operations',
    path='/auth'
)

tokens_resp_model = auth_ns.model('TokensRespModel', {
    'access_token': fields.String(
        example=('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                 'eyJ1c2VySWQiOiJiMDhmODZhZi0zNWRhLTQ4ZjItOGZhYi1jZWYzOTA0NjYwYmQifQ.'
                 '-xN_h82PHVTCMA9vdoHrcZxH-x5mb11y1537t3rGzcM')
    ),
    'refresh_token': fields.String(
        example=('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                 'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.'
                 'SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')
    ),
})

ue_ref_token_error_resp_model = auth_ns.model("UnEntityRespModel", {
    "msg": fields.String(
        example="Only refresh tokens are allowed"
    )
})

u_id_miss_model = auth_ns.model('UidMissErrorModel', {
    'message': fields.String(
        example='missing user_id in token claims.'
    )
})


@auth_ns.route('/login')
class Login(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()
        self.token_service = get_tokens_service()
        self.auth_history_service = get_auth_history_service()

    decorators = [limiter.limit("30/minute")]

    class PostReqSchema(Schema):
        login = ma_fields.String(
            required=True,
            validate=validate.Email(error="Not a valid email address")
        )
        password = ma_fields.String(
            required=True,
            load_only=True,
            validate=[validate.Length(min=6)]
        )

    post_req_schema = PostReqSchema()

    post_req_model = auth_ns.model('LoginPostReqModel', {
        'login': fields.String(
            description='User email', required=True, example='squirrelmail@gmail.com'
        ),
        'password': fields.String(
            description='User password', required=True, example='P4$$w0rd!'
        ),
    })

    post_resp_cred_error_model = auth_ns.model('LoginCredErrorRespModel', {
        'errors': fields.String(example='Bad credentials')
    })

    post_resp_valid_error_model = auth_ns.model('LoginValidErrorRespModel', {
        'errors': fields.Nested(
            auth_ns.model('LoginErrorsRespModel', {
                'login': fields.List(fields.String(example='Not a valid email address'))
            }
                          )
        )
    })



    @auth_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', tokens_resp_model),
            HTTPStatus.BAD_REQUEST: (
                    'Validation error', post_resp_valid_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                    'Credentials error', post_resp_cred_error_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', internal_error_model
            )
        }
    )
    @auth_ns.expect(post_req_model)
    @jaeger_trace(
        {
            'span_name': "auth login POST view",
        },
        tracer
    )
    def post(self):
        """
        Authenticate user and return tokens
        """
        json_input = request.get_json()
        try:
            data = self.post_req_schema.load(json_input)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        auth_ns.logger.info(f"User {data['login']} is trying to authenticate")

        verified_user = self.user_service.is_user_verified(
            data['login'],
            data['password']
        )
        if not verified_user:
            return {"error": "Bad credentials"}, HTTPStatus.UNAUTHORIZED

        access_token = self.token_service.create_user_access_token(
            verified_user
        )
        refresh_token = self.token_service.create_user_refresh_token(
            verified_user
        )
        self.token_service.add_refresh_token_to_db(
            verified_user,
            refresh_token,
            request.headers.get('User-Agent')
        )

        self.auth_history_service.add_auth_attempt_to_db(
            verified_user,
            request.remote_addr,
            request.headers.get('User-Agent')
        )

        return {
                   "access_token": access_token, "refresh_token": refresh_token
               }, HTTPStatus.OK


@auth_ns.route('/refresh')
class Refresh(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.token_service = get_tokens_service()

    @auth_ns.doc(
        responses={
            HTTPStatus.OK: ("Success", tokens_resp_model),
            HTTPStatus.UNPROCESSABLE_ENTITY: (
                    "Unprocessable entity", ue_ref_token_error_resp_model
            ),
            HTTPStatus.UNAUTHORIZED: ("Unauthorized", unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    "Internal error", internal_error_model
            ),
            HTTPStatus.BAD_REQUEST: (
                    "Bad request", u_id_miss_model
            )
        }
    )
    @auth_ns.expect(token_in_headers)
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh access and refresh tokens by refresh token
        """
        user = self.token_service.get_user_from_token_claims(
            claims=get_jwt_identity()
        )
        if not user:
            abort(HTTPStatus.UNAUTHORIZED, "User in claims is missing.")

        auth_ns.logger.info(
            f"User {user.id} is trying update tokens. Agent: {request.headers.get('User-Agent')}"
        )

        # checking that this refresh token is still relevant
        old_token = self.token_service.check_refresh_token_relevance(
            user.id,
            request.headers.get('User-Agent'),
            request.headers.get('Authorization').split()[1]
        )
        if not old_token:
            abort(HTTPStatus.UNAUTHORIZED,
                  'This refresh token is no longer available')

        access_token = self.token_service.create_user_access_token(
            user
        )
        refresh_token = self.token_service.create_user_refresh_token(
            user
        )

        self.token_service.add_refresh_token_to_db(
            user,
            refresh_token,
            request.headers.get('User-Agent')
        )

        return {
                   "access_token": access_token, "refresh_token": refresh_token
               }, HTTPStatus.OK


@auth_ns.route('/revoke_access')
class RevokeAccess(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.token_service = get_tokens_service()

    s_resp_model = auth_ns.model('RevokeAccessSRespModel', {
        'msg': fields.String(
            example="Access token was successfully revoked"
        )
    })

    @auth_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', s_resp_model),
            HTTPStatus.UNAUTHORIZED: ('Unauthorized', unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', internal_error_model
            ),
        }
    )
    @auth_ns.expect(token_in_headers)
    @jwt_required(refresh=False)
    def delete(self):
        """Revoke an access token"""
        self.token_service.revoke_access_token(
            get_jwt()
        )
        return {"msg": "Access token was successfully revoked"}, HTTPStatus.OK


@auth_ns.route('/revoke_refresh')
class RevokeRefresh(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.token_service = get_tokens_service()

    s_resp_model = auth_ns.model('RevokeRefreshSRespModel', {
        'msg': fields.String(
            example="Refresh token was successfully revoked"
        )
    })

    @auth_ns.doc(
        responses={
            HTTPStatus.OK: ("Success", s_resp_model),
            HTTPStatus.UNPROCESSABLE_ENTITY: (
                    "Unprocessable entity", ue_ref_token_error_resp_model
            ),
            HTTPStatus.UNAUTHORIZED: ("Unauthorized", unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    "Internal error", internal_error_model
            ),
            HTTPStatus.BAD_REQUEST: (
                    "Bad request", u_id_miss_model
            )
        }
    )
    @auth_ns.expect(token_in_headers)
    @jwt_required(refresh=True)
    def delete(self):
        """Revoke a refresh token (logout)."""
        self.token_service.revoke_refresh_token(
            get_jwt(),
            request.headers.get('User-Agent'),
            request.headers.get('Authorization').split()[1]
        )
        return {"msg": "Refresh token was successfully revoked"}, HTTPStatus.OK
