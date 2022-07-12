from http import HTTPStatus

from flask import jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from views.resp_models import internal_error_model, unauth_error_resp_model

check_token_ns = Namespace(
    'CheckRoles',
    description='Validate jwt token and return user roles.',
    path='/auth'
)


@check_token_ns.route('/check_roles', doc=False)
class CheckRoles(Resource):

    post_resp_model = check_token_ns.model('CheckRolesRespModel', {
        'message': fields.String(
            example=['subscription'])
    })

    @check_token_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', post_resp_model),

            HTTPStatus.UNAUTHORIZED: (
                    'error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', internal_error_model
            )
        }
    )
    @check_token_ns.param(
        name='Authorization',
        description='jwt token in format "Bearer {jwt}"',
        _in='header')
    @jwt_required(locations='headers')
    def get(self):
        roles = get_jwt().get('sub', {}).get('user_roles')
        if not roles:
            roles = ["not_subscription"]
        return jsonify({"user_roles": roles})
