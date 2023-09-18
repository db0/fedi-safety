import time
import uuid
import json
from loguru import logger
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_, not_, Boolean
from sqlalchemy.orm import noload
from fedi_safety_api.flask import db
from fedi_safety_api.utils import hash_api_key
from sqlalchemy.orm import joinedload
from fedi_safety_api.classes.request import ScanRequest
from fedi_safety_api import enums

def find_waiting_scan_request():
    query = ScanRequest.query.filter(
        ScanRequest.state == enums.State.WAITING,
    ).order_by(
        ScanRequest.created.asc()
    ).with_for_update(
        skip_locked=True, 
        of=ScanRequest
    )
    return query.first()

def find_scan_request_by_name(image_name: str):
    query = ScanRequest.query.filter(
        ScanRequest.image == image_name,
    )
    return query.first()

def find_scan_request_by_id(scan_id):
    query = ScanRequest.query.filter(
        ScanRequest.id == scan_id,
    )
    return query.first()