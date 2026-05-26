from sqlalchemy.sql import func
from datetime import datetime
from database import db
from infrastructure.database.models.player import Player

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    player1_id = db.Column(db.BigInteger, db.ForeignKey('players.id'), nullable=False)
    player2_id = db.Column(db.BigInteger, db.ForeignKey('players.id'), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #Relationship
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])

    def __init__(self, id, player1_id, player2_id, ranking):
        super().__init__()
        self.id = id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.ranking = ranking

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['insId'],
            player1_id=data['jouId1'],
            player2_id=data['jouId2'],
            ranking=data['poidsInscription'])

    def to_dict(self):
        return {
            'fftId': self.id,
            'player1Id': self.player1_id,
            'player2Id': self.player2_id,
            'ranking': self.ranking
        }
