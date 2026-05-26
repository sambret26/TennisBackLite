from datetime import datetime
from database import db

class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    category = db.Column(db.String, nullable=False)
    channel_type = db.Column(db.String)
