from flask_restx import Namespace


req_models = Namespace(
    'Request models',
    description='Request models',
)

token_in_headers = req_models.parser()
token_in_headers.add_argument(
    'Authorization',
    location='headers',
)
