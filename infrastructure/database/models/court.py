from datetime import datetime
from database import db

class Court(db.Model):
    __tablename__ = 'courts'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['courtId'],
            name=data['nomDuCourt'],
            number=data['ordre'])

    def to_dict(self):
        return {
            'fftId': self.id,
            'name': self.name,
            'number': self.number
        }
