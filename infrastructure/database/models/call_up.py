from datetime import datetime
from sqlalchemy.sql import func

from database import db


class CallUp(db.Model):
    __tablename__ = 'call_ups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    call_up_id = db.Column(db.String, nullable=False, unique=True)
    crm_id = db.Column(db.BigInteger, nullable=False)
    match_id = db.Column(db.BigInteger, nullable=False)
    state = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @classmethod
    def from_fft(cls, data):
        return cls(
            call_up_id=data['conId'],
            crm_id=data['crmId'],
            match_id=data['matId'],
            state=data['statutConvocationCode'])