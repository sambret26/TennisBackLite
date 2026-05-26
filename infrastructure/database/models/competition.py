from datetime import datetime
from sqlalchemy.sql import func

from database import db


class Competition(db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.BigInteger, primary_key=True)
    label = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @classmethod
    def from_fft(cls, data):
        return cls(
            id = data['homId'],
            label=data['libelle'],
            active = False,
            start_date=data['dateDebut'],
            end_date=data['dateFin'])

    def are_different(self, competition):
        return (self.label != competition.label or
                self.start_date != competition.start_date or
                self.end_date != competition.end_date)

    def to_dict(self):
        return {
            'homologationId': self.id,
            'label': self.label,
            'isActive': self.active,
            'startDate': self.start_date,
            'endDate': self.end_date,
        }

    def to_dict_for_db(self):
        return {
            'label': self.label,
            'id': self.id,
            'start_date': self.start_date,
            'end_date': self.end_date
        }