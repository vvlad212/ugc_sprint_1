from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request
from flask_restx import abort
from flask import session


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            roles = get_jwt().get('sub', {}).get('user_roles')
            if roles:
                if 'admin' in roles:
                    return fn(*args, **kwargs)
            return abort(HTTPStatus.FORBIDDEN, 'Admins only!')
        return decorator
    return wrapper
