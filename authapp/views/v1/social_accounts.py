from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, ValidationError
from marshmallow import fields as ma_fields

from services.social_networks_service import get_soc_networks_service
from views.req_models import token_in_headers
from views.resp_models import internal_error_model, unauth_error_resp_model

soc_ns = Namespace(
    'Social accounts',
    description="Operations with user's social accounts.",
    path='/soc'
)


@soc_ns.route('/')
class SocNetwork(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.soc_n_service = get_soc_networks_service()

    class DeleteSocNetworkReqSchema(Schema):
        soc_network_id = ma_fields.UUID(
            required=True,
            example='c184f97f-ddb0-41a4-90ec-f09e8e4c3b97'
        )
    delete_soc_req_schema = DeleteSocNetworkReqSchema()

    delete_req_model = soc_ns.model('DeleteSocReqModel', {
        'soc_network_id': fields.String(
            required=True,
            example='c184f97f-ddb0-41a4-90ec-f09e8e4c3b97',
        ),
    })

    delete_resp_valid_error_model = soc_ns.model('DeleteSocValidErrorRespModel', {
        'errors': fields.Nested(
            soc_ns.model('DeleteSocErrorsRespModel', {
                'soc_network_id': fields.List(
                    fields.String(
                        example=(
                            "Missing data for required field.",
                            "Not a valid UUID."
                        )
                    )
                )
            }
            )
        )
    })

    @soc_ns.doc(
        responses={
            int(HTTPStatus.OK): 'Success',
            int(HTTPStatus.BAD_REQUEST): (
                'Validation error', delete_resp_valid_error_model
            ),
            int(HTTPStatus.UNAUTHORIZED): (
                'Credentials error', unauth_error_resp_model
            ),
            int(HTTPStatus.INTERNAL_SERVER_ERROR): (
                'Internal error', internal_error_model
            ),
            int(HTTPStatus.NO_CONTENT): "No content",
        }
    )
    @soc_ns.expect(delete_req_model, token_in_headers)
    @jwt_required()
    def delete(self):
        """
        Remove user social network account from db by id
        """
        json_input = request.get_json()
        try:
            data = self.delete_soc_req_schema.load(json_input)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        soc_ns.logger.info(
            f"User:{get_jwt_identity().get('user_id')} is trying to remove social network account:{data['soc_network_id']}"
        )

        if not self.soc_n_service.delete_user_soc(
            data['soc_network_id']
        ):
            return '', HTTPStatus.NO_CONTENT

        return HTTPStatus.OK
