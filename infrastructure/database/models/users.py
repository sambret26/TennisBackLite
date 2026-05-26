from sqlalchemy.sql import func
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile = db.Column(db.Integer, nullable=False)
    super_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.profile = 0
        self.super_admin = 0

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data['username'],
            password=data['password']
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'profileValue': self.profile,
        }
