from flask import Blueprint
from flask_restx import Api
from importlib import import_module

from fedi_safety_api.apis.v1 import api as v1

blueprint = Blueprint('apiv1', __name__, url_prefix='/api')
api = Api(blueprint,
    version='1.0', 
    title=f'Fediseer',
    description=f'The API documentation for the Fediseer',
    contact_email="mail@dbzer0.com",
    default="v1",
    default_label="Latest Version",
    ordered=True,
)

api.add_namespace(v1)
