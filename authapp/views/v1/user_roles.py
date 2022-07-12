import datetime
from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields, marshal, reqparse
from marshmallow import Schema, ValidationError
from marshmallow import fields as ma_fields

from services.roles_service import get_roles_service
from views.req_models import token_in_headers
from views.resp_models import (
    internal_error_model,
    unauth_error_resp_model, admin_error_resp_model
)
from views.views_decorators import admin_required

user_roles_ns = Namespace(
    'UserRoles',
    description='Operations with user roles',
    path='/user_roles'
)


@user_roles_ns.route('/')
class UserRoles(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.roles_service = get_roles_service()

    class PostReqSchema(Schema):
        user_id = ma_fields.UUID(
            required=False,
        )

    post_req_schema = PostReqSchema()

    get_user_roles_req_model = reqparse.RequestParser()
    get_user_roles_req_model.add_argument(
        "user_id",
        type=str,
        required=False,
    )

    get_user_roles_resp_model = user_roles_ns.model('GetUserRolesRespModel', {
        'role_name': fields.String(example="user role"),
        'assignment_timestamp': fields.DateTime(example="2018-01-02T22:08:12.510696")
    })
    get_user_roles_resp_model_list = user_roles_ns.model('GetUserRolesRespModelList', {
        "user_roles": fields.List(fields.Nested(get_user_roles_resp_model))
    })

    admin_req_u_id_miss_model = user_roles_ns.model('AdminUidMissRespModel', {
        "message": fields.String("user_id is missing in request json params"),
    })

    @user_roles_ns.doc(
        responses={
            HTTPStatus.OK: ("Success", get_user_roles_resp_model_list),
            HTTPStatus.UNAUTHORIZED: ("Unauthorized", unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                    "Internal error", internal_error_model
            ),
            HTTPStatus.BAD_REQUEST: (
                    "Bad request", admin_req_u_id_miss_model
            )
        }
    )
    @user_roles_ns.expect(get_user_roles_req_model, token_in_headers)
    @jwt_required()
    def get(self):
        """
        Get roles of user
        """
        roles = get_jwt().get('sub', {}).get('user_roles', [])
        user_id_claims = get_jwt_identity().get('user_id')
        if 'admin' in roles:
            try:
                data = self.post_req_schema.load(request.args)
                user_id = data.get('user_id')
                if not user_id:
                    raise (
                        ValidationError(
                            "user_id is required for req with admin token."
                        )
                    )
            except ValidationError as err:
                return {"errors": err.messages}, HTTPStatus.BAD_REQUEST
        else:
            user_id = user_id_claims

        user_roles_ns.logger.info(
            f"User:{user_id_claims} is trying to get roles of user:{user_id}"
        )

        return marshal(
            {"user_roles": self.roles_service.get_user_roles(user_id)},
            self.get_user_roles_resp_model_list
        ), HTTPStatus.OK

    class AddRoleReqSchema(Schema):
        user_id = ma_fields.UUID(
            required=False,
            example='c184f97f-ddb0-41a4-90ec-f09e8e4c3b97'
        )
        role_id = ma_fields.String(
            required=False,
            example='cefd32f0-aef6-490a-bbb1-0037d4c2f043'
        )

    add_role_req_schema = AddRoleReqSchema()

    post_add_user_roles_req_model = reqparse.RequestParser()
    post_add_user_roles_req_model.add_argument("user_id", type=str, required=False)
    post_add_user_roles_req_model.add_argument("role_id", type=str, required=False)

    post_user_add_role_resp_model = user_roles_ns.model('PostAddUserRolesRespModel', {
        'message': fields.String(example="role add"),
        'assignment_timestamp': fields.DateTime(example="2018-01-02T22:08:12.510696")
    })

    add_user_roles_resp_bad_req_model = user_roles_ns.model(
        'AddRoleToUserBadReqModel',
        {
            "message": fields.String(
                example=(
                    "Role is missing in db.",
                    "Token has been revoked",
                    "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'",
                    "User_id is missing in db."
                )
            )
        }
    )


    @user_roles_ns.doc(
        responses={
            HTTPStatus.OK: ("Success", post_user_add_role_resp_model),
            HTTPStatus.UNAUTHORIZED: ("Unauthorized", unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: ("Internal error", internal_error_model),
            HTTPStatus.BAD_REQUEST: ("Bad request", add_user_roles_resp_bad_req_model),
            HTTPStatus.FORBIDDEN: ('Forbidden', admin_error_resp_model),
        }
    )
    @user_roles_ns.expect(post_add_user_roles_req_model, token_in_headers)
    @admin_required()
    def post(self):
        """
        Add role to user
        """
        data = self.add_role_req_schema.load(request.args)
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        if not user_id:
            raise (ValidationError("user_id is required for req with admin token."))
        else:
            try:
                self.roles_service.add_role_to_user(user_id, role_id)
            except ValidationError as err:
                return {'message': err.messages}, HTTPStatus.NOT_FOUND
        user_roles_ns.logger.info(
            f"User:{user_id} is trying to add role of user:{user_id}"
        )
        return {"message": f'The {role_id} role has been added to the user {user_id}',
                "assignment_timestamp": str(datetime.datetime.now())}, HTTPStatus.OK

    class DeleteRoleReqSchema(Schema):
        user_id = ma_fields.UUID(
            required=False,
            example='c184f97f-ddb0-41a4-90ec-f09e8e4c3b97'
        )
        role_id = ma_fields.String(
            required=False,
            example='cefd32f0-aef6-490a-bbb1-0037d4c2f043'
        )

    delete_role_req_schema = DeleteRoleReqSchema()

    delete_add_user_roles_req_model = reqparse.RequestParser()
    delete_add_user_roles_req_model.add_argument("user_id", type=str, required=False, )
    delete_add_user_roles_req_model.add_argument("role_id", type=str, required=False)

    delete_user_roles_resp_model = user_roles_ns.model('PostAddUserRolesRespModel', {
        'message': fields.String(example='The {role_id} role has been deleted to the user {user_id}'),
        'assignment_timestamp': fields.DateTime(example="2018-01-02T22:08:12.510696")
    })

    delete_user_roles_resp_bad_req_model = user_roles_ns.model(
        'DeleteRoleToUserBadReqModel',
        {
            "message": fields.String(
                example=(
                    "Missing Authorization Header",
                    "Token has been revoked",
                    "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'"
                )
            )
        }
    )

    @user_roles_ns.doc(
        responses={
            HTTPStatus.OK: ("Success", get_user_roles_resp_model_list),
            HTTPStatus.UNAUTHORIZED: ("Unauthorized", unauth_error_resp_model),
            HTTPStatus.INTERNAL_SERVER_ERROR: ("Internal error", internal_error_model),
            HTTPStatus.BAD_REQUEST: ("Bad request", delete_user_roles_resp_bad_req_model),
            HTTPStatus.FORBIDDEN: ('Forbidden', admin_error_resp_model),
        }
    )
    @user_roles_ns.expect(delete_add_user_roles_req_model, token_in_headers)
    @admin_required()
    def delete(self):
        """
        Delete role to user
        """
        data = self.delete_role_req_schema.load(request.args)
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        if not user_id:
            raise (ValidationError("user_id is required for req with admin token."))
        else:
            try:
                self.roles_service.delete_role_to_user(user_id, role_id)
            except ValidationError as err:
                return {'message': err.messages}, HTTPStatus.NOT_FOUND
            except Exception as err:
                return {'message': err}, HTTPStatus.NOT_FOUND
        user_roles_ns.logger.info(
            f"User:{user_id} is trying to delete role of user:{user_id}"
        )
        return {"message": f'The {role_id} role has been deleted to the user {user_id}',
                "assignment_timestamp": str(datetime.datetime.now())}, HTTPStatus.OK
