from flask_restx import Api

from views.v1.social_accounts import soc_ns
from views.v1.auth.auth import auth_ns
from views.v1.auth.yandex_auth import yandex_auth_ns
from views.v1.change_credentials import change_credentials_ns
from views.v1.auth.google_auth import auth_google_ns
from views.v1.check_roles import check_token_ns
from views.v1.registration import registration_ns
from views.v1.auth_history import auth_history_ns
from views.v1.roles import roles_ns
from views.v1.user_roles import user_roles_ns
from views.resp_models import errors
from views.req_models import req_models


def register_routes(api: Api):
    # errors models
    api.add_namespace(errors)
    # req models
    api.add_namespace(req_models)
    # google OAuth
    api.add_namespace(auth_google_ns)
    # auth
    api.add_namespace(auth_ns)
    # ya auth
    api.add_namespace(yandex_auth_ns)
    # reg
    api.add_namespace(registration_ns)
    # auth history
    api.add_namespace(auth_history_ns)
    # roles
    api.add_namespace(roles_ns)
    # user roles
    api.add_namespace(user_roles_ns)
    # change user credentials
    api.add_namespace(change_credentials_ns)
    # validate token
    api.add_namespace(check_token_ns)
    # social networks
    api.add_namespace(soc_ns)

