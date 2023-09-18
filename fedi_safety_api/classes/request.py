import dateutil.relativedelta
from datetime import datetime

from loguru import logger
from fedi_safety_api.flask import db


class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text, unique=False, nullable=False, index=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_csam = db.Column(db.Boolean, nullable=True)
    is_nsfw = db.Column(db.Boolean, nullable=True)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
