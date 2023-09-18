from dotenv import load_dotenv
import os
import logging

load_dotenv()

from fedi_safety_api.argparser import args
from fedi_safety_api.flask import APP
from loguru import logger

if __name__ == "__main__":
    # Only setting this for the WSGI logs
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.DEBUG)
    from waitress import serve

    logger.init("WSGI Server", status="Starting")
    url_scheme = 'https'
    if args.insecure:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Disable this on prod
        url_scheme = 'http'
    allowed_host = "127.0.0.1"
    if args.insecure:
        allowed_host = "0.0.0.0"
        logger.init_warn("WSGI Mode", status="Insecure")
    serve(APP, port=args.port, url_scheme=url_scheme, threads=45, connection_limit=1024, asyncore_use_poll=True)
    logger.init("WSGI Server", status="Stopped")
