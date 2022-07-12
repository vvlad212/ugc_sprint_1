from http import HTTPStatus

import flask_jwt_extended
from flask import jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from services.auth_history_service import get_auth_history_service
from views.resp_models import internal_error_model, unauth_error_resp_model

auth_history_ns = Namespace(
    'AuthHistory',
    description='Getting authorization history.',
    path='/auth'
)


@auth_history_ns.route('/history')
class AuthHistory(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.auth_history_service = get_auth_history_service()

    post_resp_model = auth_history_ns.model('AuthHistoryRespModel', {
        'message': fields.String(
            example=[['Sun, 19 Jun 2022 07:59:07 GMT', 'werkzeug/2.1.2', '127.0.0.1'],
                     ['Sun, 19 Jun 2022 07:59:08 GMT', 'werkzeug/2.1.2', '127.0.0.1']])
    })

    unprocessable_error_model = auth_history_ns.model('AuthHistInternalErrorModel', {
        'msg': fields.String(
            example="Not enough segments")
    })

    @auth_history_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', post_resp_model),

            HTTPStatus.UNAUTHORIZED: (
                    'error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    'Internal error', internal_error_model
            ),
            HTTPStatus.UNPROCESSABLE_ENTITY: (
                    'error', unprocessable_error_model
            )
        }
    )
    @auth_history_ns.param(
        name='Authorization',
        description='jwt token in format "Bearer {jwt}"',
        _in='header')
    @jwt_required(locations='headers')
    def get(self):
        user_id = flask_jwt_extended.get_jwt_identity().get('user_id')
        if not user_id:
            return {"errors": f'failed to get user_id field from token'}, HTTPStatus.BAD_REQUEST

        auth_history = self.auth_history_service.get_auth(user_id=user_id)
        return jsonify({"message": auth_history})
