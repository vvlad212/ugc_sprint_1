from flask_restx import Namespace, fields


errors = Namespace(
    'Errors',
    description='Errors models',
)

internal_error_model = errors.model('InternalErrorModel', {
    'message': fields.String(
        example=(
            'The server encountered an internal error'
            'and was unable to complete your request. Either the server'
            'is overloaded or there is an error in the application.'
        )
    )
})

unauth_error_resp_model = errors.model("UnauthRespModel", {
    "msg": fields.String(
        example=("Missing Authorization Header", "Token has been revoked"),
    )
})

admin_error_resp_model = errors.model("NotAdminRespModel", {
    "message": fields.String(
        example="Admins only!",
    )
})

