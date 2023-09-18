import os
from PIL import Image
from io import BytesIO
from werkzeug.datastructures import FileStorage
from flask import request
from flask_restx import Namespace, Resource, reqparse
from fedi_safety_api.flask import cache, db
from loguru import logger
from fedi_safety_api.classes.request import Request
from fedi_safety_api.database import functions as database
from fedi_safety_api import exceptions as e

api = Namespace('v1', 'API Version 1' )

from fedi_safety_api.apis.models.v1 import Models

models = Models(api)

handle_bad_request = api.errorhandler(e.BadRequest)(e.handle_bad_requests)
handle_forbidden = api.errorhandler(e.Forbidden)(e.handle_bad_requests)
handle_unauthorized = api.errorhandler(e.Unauthorized)(e.handle_bad_requests)
handle_not_found = api.errorhandler(e.NotFound)(e.handle_bad_requests)
handle_too_many_requests = api.errorhandler(e.TooManyRequests)(e.handle_bad_requests)
handle_internal_server_error = api.errorhandler(e.InternalServerError)(e.handle_bad_requests)
handle_service_unavailable = api.errorhandler(e.ServiceUnavailable)(e.handle_bad_requests)

# Used to for the flask limiter, to limit requests per url paths
def get_request_path():
    # logger.info(dir(request))
    return f"{request.remote_addr}@{request.method}@{request.path}"


class Scan(Resource):
    post_parser = api.parser()
    post_parser.add_argument("Content-Type", type=str, required=False, help="The file's media type.", location="headers")
    post_parser.add_argument('file', location='files', type=FileStorage, required=False)

    @api.expect(post_parser)
    def post(self):
        '''Scan an image
        '''
        # I don't get why this is not using the import from earlier...
        from fedi_safety_api import exceptions as e
        self.args = self.post_parser.parse_args()
        file = self.args["file"]
        if not file:
            raise e.BadRequest("No file provided")
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            raise e.BadRequest("Invalid file format")
        try:
            img_data = BytesIO(file.read())
            img = Image.open(img_data)
        except Exception as e:
            raise e.InternalServerError(f"something went wrong: {e}")
        return {"message": "Image processed successfully"},200
