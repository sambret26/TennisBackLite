from datetime import datetime
from database import db

class Url(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    url = db.Column(db.String)
