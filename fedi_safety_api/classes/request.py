import dateutil.relativedelta
from datetime import datetime
from sqlalchemy import Enum, UniqueConstraint

from loguru import logger
from fedi_safety_api.flask import db
from fedi_safety_api import enums


class ScanRequest(db.Model):
    __tablename__ = "scan_requests"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text, unique=False, nullable=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column(Enum(enums.State), default=enums.State.WAITING, nullable=False)
    is_csam = db.Column(db.Boolean, nullable=True)
    is_nsfw = db.Column(db.Boolean, nullable=True)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
