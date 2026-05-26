from sqlalchemy.sql import func
from datetime import datetime
from database import db

class Ranking(db.Model):
    __tablename__ = 'rankings'

    id = db.Column(db.BigInteger, primary_key=True)
    simple = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['echelon'],
            simple=data['libelle'].replace(' ',''))

    def to_dict(self):
        return {
            'fftId': self.id,
            'simple': self.simple
        }