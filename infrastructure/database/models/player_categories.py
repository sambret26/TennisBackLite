from sqlalchemy.sql import func
from datetime import datetime
from database import db

class PlayerCategories(db.Model):
    __tablename__ = 'player_categories'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    player_id = db.Column(db.BigInteger, db.ForeignKey('players.id'), nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __init__(self, player_id, category_id):
        super().__init__()
        self.player_id = player_id
        self.category_id = category_id