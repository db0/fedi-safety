import os
import time
from PIL import Image
from io import BytesIO
from werkzeug.datastructures import FileStorage
from flask import request, send_file
from flask_restx import Namespace, Resource, reqparse
from fedi_safety_api.flask import cache, db
from loguru import logger
from fedi_safety_api.classes.request import ScanRequest
from fedi_safety_api.database import functions as database
from fedi_safety_api import exceptions as e
from fedi_safety_api import enums

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
        self.filename = f"{os.getenv('FEDIVERSE_SAFETY_IMGDIR')}/{file.filename}"
        try:
            img_data = BytesIO(file.read())
            img = Image.open(img_data)
            img.save(self.filename)
            new_request = ScanRequest(
                image = file.filename
            )
            db.session.add(new_request)
            db.session.commit()
            retries = 0
            while new_request.state in [enums.State.PROCESSING, enums.State.WAITING]:
                db.session.refresh(new_request)
                retries += 1
                logger.debug([new_request,new_request.state])
                if retries > int(os.getenv('FEDIVERSE_SAFETY_TIME_THRESHOLD', 120)):
                    os.remove(self.filename)
                    db.session.delete(new_request)
                    db.session.commit()
                    return {"message": "Could not scan request in reasonable amount of time. Returning OK"}, 200
                time.sleep(1)
            logger.debug(new_request.state)
            os.remove(self.filename)
            if new_request.state == enums.State.FAULTED:
                db.session.delete(new_request)
                db.session.commit()
                return {"message": "Faulted request. Returning OK"}, 200 
            if new_request.state == enums.State.DONE:
                if new_request.is_csam == True:
                    db.session.delete(new_request)
                    db.session.commit()
                    return {"message": "Potential CSAM Image detected"}, 406
                else: 
                    db.session.delete(new_request)
                    db.session.commit()
                    return {"message": "Image OK"}, 200 
            else:
                db.session.delete(new_request)
                db.session.commit()
                logger.error(f"Image with state {new_request.state} detected!")
                return {"message": "Should not be here. Returning OK"},200
        except Exception as err:
            db.session.delete(new_request)
            db.session.commit()
            logger.error(f"Exception while processing scan {err}")
            return {"message": "Something went wrong internally. Returning OK"}, 200

class Pop(Resource):
    get_parser = api.parser()
    get_parser.add_argument("apikey", type=str, required=True, help="The auth api key", location="headers")

    @api.expect(get_parser)
    def get(self):
        '''Pick up an image to safety validate
        '''
        # I don't get why this is not using the import from earlier...
        self.args = self.get_parser.parse_args()
        if os.getenv("FEDIVERSE_SAFETY_WORKER_AUTH") != self.args.apikey:
            raise e.Forbidden("Access Denied")
        pop: ScanRequest = database.find_waiting_scan_request()
        if not pop:
            return {"message": "Nothing to do"},204
        pop.state = enums.State.PROCESSING
        db.session.commit()
        return send_file(f"{os.getenv('FEDIVERSE_SAFETY_IMGDIR')}/{pop.image}", as_attachment=True, download_name=pop.image)

    post_parser = api.parser()
    post_parser.add_argument("apikey", type=str, required=True, help="The auth api key", location="headers")
    post_parser.add_argument("image", type=str, required=True, help="The image filename", location="json")
    post_parser.add_argument("is_csam", type=bool, required=True, help="Is this image csam?", location="json")
    post_parser.add_argument("is_nsfw", type=bool, required=True, help="Is this image nsfw?", location="json")

    @api.expect(post_parser)
    def post(self):
        '''Submit an image result
        '''
        # I don't get why this is not using the import from earlier...
        self.args = self.post_parser.parse_args()
        if os.getenv("FEDIVERSE_SAFETY_WORKER_AUTH") != self.args.apikey:
            raise e.Forbidden("Access Denied")
        pop: ScanRequest = database.find_scan_request_by_name(self.args.image)
        if not pop:
            raise e.NotFound("No image found waiting for this result.")
        pop.is_csam = self.args.is_csam
        pop.is_nsfw = self.args.is_nsfw
        pop.state = enums.State.DONE
        db.session.commit()
        return {"message": "OK"},201
