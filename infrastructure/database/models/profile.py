from datetime import datetime
from database import db

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'value': self.value
        }