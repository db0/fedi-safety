import fedi_safety_api.apis.v1.base as base
from fedi_safety_api.apis.v1.base import api

api.add_resource(base.Scan, "/scan")
api.add_resource(base.Pop, "/pop")
