import re
from http import HTTPStatus

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, ValidationError, fields as ma_fields

from models.user import User
from services.user_service import get_user_service
from views.resp_models import internal_error_model, unauth_error_resp_model

change_credentials_ns = Namespace(
    'ChangeCredentials',
    description='Changing user credentials (login, password)',
    path='/change_credentials'
)


def validate_password(password: str):
    """Валидация пароля по регулярному выражению."""
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#/.?&])[A-Za-z\d@$!%*#/.?&]{6,}$'
    if not re.match(pattern, password):
        raise ValidationError('Password has incorrect format.')


def validate_login(email: str):
    """Валидация логина проверка на существование и то что это email."""
    if User.query.filter_by(login=email).first():
        raise ValidationError('This login already exists.')


class PostReqLoginSchema(Schema):
    login_old = ma_fields.Email(required=True)
    login_new = ma_fields.Email(required=True, validate=validate_login)
    password = ma_fields.String(required=True, validate=validate_password)


class PostReqPasswordSchema(Schema):
    login = ma_fields.Email(required=True)
    password_old = ma_fields.String(required=True, validate=validate_password)
    password_new = ma_fields.String(required=True, validate=validate_password)


@change_credentials_ns.route('/password')
class ChangePassword(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()
        self.post_req_schema = PostReqPasswordSchema()

    post_req_model = change_credentials_ns.model(
        'ChangeCredentialsPasswordReqModel',
        {
            'login': fields.String(description='User login',
                                   required=True,
                                   example='squirrelmail@gmail.com'),
            'old_password': fields.String(description='Old user password',
                                          required=True,
                                          example='P4$$w0rd!'),
            'new_password': fields.String(description='New user password',
                                          required=True,
                                          example='NewP4$$w0rd!'),
        })

    post_resp_model = change_credentials_ns.model('ChangeCredentialsRespModel',
                                                  {
                                                      'result': fields.String,
                                                  })

    resp_validation_error_model = change_credentials_ns.model(
        "ChangePasswordValidationErrorModel", {
            "error": fields.String(
                example=("Missing Authorization Header",
                         "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'",
                         "The password must be different from the current one."),
            )
        })

    resp_unprocessable_error_model = change_credentials_ns.model(
        'ChangePasswordUnprocessableErrorModel', {
            'msg': fields.String(
                example="Not enough segments")
        })


    @change_credentials_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', post_resp_model),
            HTTPStatus.BAD_REQUEST: (
                    'Validation error', resp_validation_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                    'Credentials error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', internal_error_model
            ),
            HTTPStatus.UNPROCESSABLE_ENTITY: (
                    'error', resp_unprocessable_error_model
            )
        }
    )
    @change_credentials_ns.param(
        name='Authorization',
        description='jwt token in format "Bearer {jwt}"',
        _in='header')
    @jwt_required()
    @change_credentials_ns.expect(post_req_model)
    def post(self):
        try:
            req_data = self.post_req_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, HTTPStatus.BAD_REQUEST
        login = req_data.get('login')
        new_password = req_data.get('password_new')
        old_password = req_data.get('password_old')
        try:
            self.user_service.change_user_password(login=login,
                                                   new_password=new_password,
                                                   old_password=old_password)
        except ValidationError as err:
            return {'errors': err.messages}, HTTPStatus.BAD_REQUEST
        return jsonify({"message": "The password has been changed."})


@change_credentials_ns.route('/login')
class ChangeLogin(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()
        self.post_req_schema = PostReqLoginSchema()

    post_req_model = change_credentials_ns.model(
        'ChangeCredentialsLoginReqModel', {
            'login_old': fields.String(description='User login', required=True,
                                       example='squirrelmail@gmail.com'),
            'login_new': fields.String(description='User login', required=True,
                                       example='Newsquirrelmail@gmail.com'),
            'password': fields.String(description='User pasword', required=True,
                                      example='P4$$w0rd!'),
        })

    post_resp_model = change_credentials_ns.model('ChangeCredentialsRespModel',
                                                  {
                                                      'result': fields.String,
                                                  })

    resp_validation_error_model = change_credentials_ns.model(
        "ChangeLoginValidationErrorModel", {
            "error": fields.String(
                example=("Missing Authorization Header",
                         "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'",
                         'Failed to get user_id field from token.'),
            )
        })

    resp_auth_error_model = change_credentials_ns.model(
        'ChangeAuthErrorRespModel', {
            'errors': fields.String(example="Token has been revoked")
        })
    resp_unprocessable_error_model = change_credentials_ns.model(
        'ChangeLoginUnprocessableErrorModel', {
            'msg': fields.String(
                example="Not enough segments")
        })

    resp_internal_error_model = change_credentials_ns.model(
        'ChangeLoginInternalErrorModel', {
            'message': fields.String(
                example='The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.')
        })

    @change_credentials_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', post_resp_model),
            HTTPStatus.BAD_REQUEST: (
                    'Validation error', resp_validation_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                    'Credentials error', resp_auth_error_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', resp_internal_error_model
            ),
            HTTPStatus.UNPROCESSABLE_ENTITY: (
                    'error', resp_unprocessable_error_model
            )
        }
    )
    @change_credentials_ns.param(
        name='Authorization',
        description='jwt token in format "Bearer {jwt}"',
        _in='header')
    @jwt_required()
    @change_credentials_ns.expect(post_req_model)
    def post(self):
        try:
            req_data = self.post_req_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, HTTPStatus.BAD_REQUEST
        old_login = req_data.get('login_old')
        new_login = req_data.get('login_new')
        password = req_data.get('password')

        self.user_service.change_login(old_login=old_login, new_login=new_login, password=password)
        return jsonify({"message": "The login has been changed."})
