import logging
import re
from http import HTTPStatus

from flask import jsonify, request, abort
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, ValidationError, fields as ma_fields

from models.user import User
from services.user_service import get_user_service
from views.resp_models import internal_error_model

registration_ns = Namespace(
    'Registration',
    description='Registration new users',
    path='/registration'
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


class PostReqSchema(Schema):
    login = ma_fields.Email(required=True, validate=validate_login)
    password = ma_fields.String(required=True, validate=validate_password)


@registration_ns.route('/registration')
class Registration(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()
        self.post_req_schema = PostReqSchema()

    post_req_model = registration_ns.model('RegistrationReqModel', {
        'login': fields.String(description='User email', required=True, example='squirrelmail@gmail.com'),
        'password': fields.String(description='User password', required=True, example='P4$$w0rd!'),
    })

    post_resp_model = registration_ns.model('RegistrationRespModel', {
        'result': fields.String,
    })

    @registration_ns.doc(
        responses={
            200: ('Success', post_resp_model),
            400: 'Validation Error',
            500: ('Internal error', internal_error_model)
        })
    @registration_ns.expect(post_req_model)
    def post(self):

        json_data = request.get_json()
        try:
            data = self.post_req_schema.load(json_data)
        except ValidationError as err:
            return {'errors': err.messages}, HTTPStatus.BAD_REQUEST
        self.user_service.create_user(login=data['login'], password=data['password'])
        return jsonify({"msg": "User has been added."})

