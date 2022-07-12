from http import HTTPStatus

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from flask_restx import Namespace, Resource, abort, fields
from marshmallow import Schema, ValidationError
from marshmallow import fields as ma_fields
from marshmallow import validate

from services.roles_service import get_roles_service
from views.resp_models import (
    internal_error_model,
    unauth_error_resp_model,
)
from views.req_models import token_in_headers
from views.resp_models import admin_error_resp_model
from views.views_decorators import admin_required


roles_ns = Namespace(
    'Roles',
    description='Operations with roles',
    path='/roles'
)


@roles_ns.route('/')
class Role(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.roles_service = get_roles_service()

    class PostReqSchema(Schema):
        new_role_name = ma_fields.String(
            required=True,
            validate=validate.Length(min=1, error="New role name is missing")
        )
    post_req_schema = PostReqSchema()

    post_req_model = roles_ns.model('NewRolesPostReqModel', {
        'new_role_name': fields.String(
            required=True, example='New_shiny_role'
        ),
    })

    post_resp_valid_error_model = roles_ns.model('NewRoleValidErrorRespModel', {
        'errors': fields.Nested(
            roles_ns.model('NewRolesErrorsRespModel', {
                'new_role_name': fields.List(
                    fields.String(example='New role name is missing')
                )
            }
            )
        )
    })

    role_exist_resp_model = roles_ns.model('RoleExistRespModel', {
        'message': fields.String(example='Role already exist.'),
    })

    @roles_ns.doc(
        responses={
            HTTPStatus.OK: 'Success',
            HTTPStatus.BAD_REQUEST: (
                'Validation error', post_resp_valid_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                'Credentials error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                'Internal error', internal_error_model
            ),
            HTTPStatus.FORBIDDEN: (
                'Forbidden', admin_error_resp_model
            ),
            HTTPStatus.CONFLICT: (
                'Conflict', role_exist_resp_model,
            )
        }
    )
    @roles_ns.expect(post_req_model, token_in_headers)
    @admin_required()
    def post(self):
        """
        Create new role
        """
        json_input = request.get_json()
        try:
            data = self.post_req_schema.load(json_input)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity().get('user_id')
        roles_ns.logger.info(
            f"User {user_id} is trying to create new role {data['new_role_name']}"
        )

        self.roles_service.create_role(data['new_role_name'])

        return HTTPStatus.OK

    class DeleteReqSchema(Schema):
        role_name = ma_fields.String(
            required=True,
            validate=validate.Length(min=1, error="Role name is missing")
        )
    delete_req_schema = DeleteReqSchema()

    delete_req_model = roles_ns.model('DeleteRolesReqModel', {
        'role_name': fields.String(
            required=True, example='role_to_delete'
        ),
    })

    delete_resp_valid_error_model = roles_ns.model('DeleteRoleValidErrorRespModel', {
        'errors': fields.Nested(
            roles_ns.model('DeleteRoleErrorsRespModel', {
                'role_name': fields.List(
                    fields.String(example='Role name is missing')
                )
            }
            )
        )
    })

    deleting_admin_role_resp_model = roles_ns.model('DeleteAdminRoleErrorRespModel', {
        'message': fields.String(
            example=(
                "Deleting admin role is forbidden.",
                "Admins only!"
            ),
        )
    })

    @roles_ns.doc(
        responses={
            HTTPStatus.OK: 'Success',
            HTTPStatus.BAD_REQUEST: (
                'Validation error', delete_resp_valid_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                'Credentials error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                'Internal error', internal_error_model
            ),
            HTTPStatus.FORBIDDEN: (
                'Forbidden', deleting_admin_role_resp_model
            ),
            HTTPStatus.NO_CONTENT: "No content",
        }
    )
    @roles_ns.expect(delete_req_model, token_in_headers)
    @admin_required()
    def delete(self):
        """
        Remove role from db by name
        """
        json_input = request.get_json()
        try:
            data = self.delete_req_schema.load(json_input)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity().get('user_id')
        roles_ns.logger.info(
            f"User {user_id} is trying to remove role {data['role_name']}"
        )

        if data['role_name'] == 'admin':
            abort(HTTPStatus.FORBIDDEN, "Deleting admin role is forbidden.")

        if not self.roles_service.delete_role(data['role_name']):
            return '', HTTPStatus.NO_CONTENT

        return HTTPStatus.OK

    get_all_roles_in_bd_resp_model_list = roles_ns.model('GetAllRolesInBdRespModelList', {
        "message": fields.List(fields.String(example=[
            {"7f9df985-a682-4937-a18d-5f429e172e8e": "test_role1"},
            {"cefd32f0-aef6-490a-bbb1-0037d4c2f043": "test_role2"}
        ]
        )
        )
    })

    @roles_ns.doc(
        responses={
            200: ('Success', get_all_roles_in_bd_resp_model_list),
            HTTPStatus.BAD_REQUEST: ('Validation error', post_resp_valid_error_model),
            401: ('Credentials error', unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: ('Internal error', internal_error_model),
            HTTPStatus.FORBIDDEN: ('Forbidden', admin_error_resp_model)
        }
    )
    @roles_ns.expect(token_in_headers)
    @admin_required()
    def get(self):
        """
        Get all roles
        """
        user_id = get_jwt_identity().get('user_id')
        roles_ns.logger.info(f"User {user_id} is trying to get all roles.")
        roles = self.roles_service.get_all_roles()
        return {"message": roles}, HTTPStatus.OK

    class PutReqSchema(Schema):
        new_role_name = ma_fields.String(
            required=True,
            validate=validate.Length(min=1, error="Role name is missing")
        )
        role_id = ma_fields.UUID(required=True, error="role_id is not valid")
    put_req_schema = PutReqSchema()

    put_req_model = roles_ns.model('PutRolesReqModel', {
        "new_role_name": fields.String(
            required=True, example='new_role_name'
        ),
        "role_id": fields.String(
            required=True, example="8b835174-b9e4-4254-9042-c124d4a3cce9")
    })

    put_resp_valid_error_model = roles_ns.model('UpdateRoleValidErrorRespModel', {
        'errors': fields.Nested(
            roles_ns.model('UpdateRolesErrorsRespModel', {
                'new_role_name': fields.List(
                    fields.String(example='Role name is missing')
                ),
                'role_id': fields.List(
                    fields.String(example='role_id is not valid')
                ),
            },
            )
        )
    })

    role_not_found_model = roles_ns.model('RoleIdNotFoundErrorModel', {
        'message': fields.String(
            example=(
                "Role:8b835174-b9e4-4254-9042-c124d4a3cce9 is missing in db"
            )
        )
    })

    @roles_ns.doc(
        responses={
            HTTPStatus.OK: "Success",
            HTTPStatus.BAD_REQUEST: (
                "Validation error", put_resp_valid_error_model
            ),
            HTTPStatus.UNAUTHORIZED: (
                "Credentials error", unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                "Internal error", internal_error_model
            ),
            HTTPStatus.FORBIDDEN: (
                "Forbidden", admin_error_resp_model
            ),
            HTTPStatus.NOT_FOUND: (
                "Not Found", role_not_found_model
            )
        }
    )
    @roles_ns.expect(put_req_model, token_in_headers)
    @admin_required()
    def put(self):
        """
        Update role name by role id
        """
        json_input = request.get_json()
        try:
            data = self.put_req_schema.load(json_input)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity().get('user_id')
        roles_ns.logger.info(
            f"User {user_id} is trying to update role {data['role_id']}"
        )

        if not self.roles_service.update_role(
            data['role_id'],
            data['new_role_name']
        ):
            return {
                "message": f"Role:{data['role_id']} is missing in db"
            }, HTTPStatus.NOT_FOUND

        return HTTPStatus.OK

    @roles_ns.doc(
        responses={
            200: 'Success',
            HTTPStatus.BAD_REQUEST: ('Validation error', post_resp_valid_error_model),
            401: ('Credentials error', unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: ('Internal error', internal_error_model),
            HTTPStatus.FORBIDDEN: ('Forbidden', admin_error_resp_model),
            HTTPStatus.CONFLICT: ('Conflict', role_exist_resp_model,)
        }
    )
    @roles_ns.expect(token_in_headers)
    @admin_required()
    def get(self):
        """
        Get all roles
        """
        user_id = get_jwt_identity().get('user_id')
        roles_ns.logger.info(f"User {user_id} is trying to get all roles.")
        roles = self.roles_service.get_all_roles()
        return jsonify({"message": roles})
