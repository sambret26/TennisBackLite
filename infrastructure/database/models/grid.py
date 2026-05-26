from sqlalchemy.sql import func
from datetime import datetime
from database import db

class Grid(db.Model):
    __tablename__ = 'grids'

    id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String)
    grid_type = db.Column(db.String, nullable=False)
    table_id = db.Column(db.BigInteger)
    next_grid_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #Relationship
    category = db.relationship('Category', foreign_keys=[category_id])

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['decId'],
            category_id=data['eprId'],
            name=data['nomDecoupage'],
            code=0,
            grid_type=data['typeDecoupageCode'],
            table_id=data['tableauActifId'],
            next_grid_id=data['decoupageSuivantId'])