from sqlalchemy.sql import func
from datetime import datetime
from database import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.BigInteger, primary_key=True, index=True)
    code = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['eprId'],
            code=data['natureCategorieEpreuve'],
            label=data['libelle'])