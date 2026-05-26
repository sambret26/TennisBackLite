from sqlalchemy.sql import func
from datetime import datetime

from database import db

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.BigInteger, primary_key=True)
    crm_id = db.Column(db.BigInteger, unique=True)
    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    ranking_id = db.Column(db.BigInteger, db.ForeignKey('rankings.id'))
    club =db.Column(db.String)
    phone_number = db.Column(db.String)
    email = db.Column(db.String)
    to_delete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #Relationship
    ranking = db.relationship('Ranking')
    categories = db.relationship('Category', secondary='player_categories', lazy='joined')

    @classmethod
    def from_fft(cls, data):
        return cls(
            id=data['jouId'],
            crm_id=data['idCrm'],
            first_name=data['prenom'].title(),
            ranking_id=data['echelonSimpleUpdated'],
            last_name=data['nom'].title(),
            club=data['clubLibelle'],
            phone_number=data['numTel'],
            email=data['mail'])

    def to_dict_for_db(self):
        return{
            'id': self.id,
            'crm_id': self.crm_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'ranking_id': self.ranking_id,
            'club': self.club,
            'phone_number': self.phone_number,
            'email': self.email,
            'to_delete': self.to_delete
        }

    def to_dict(self):
        dictionary = self.to_dict_for_db()
        dictionary["fullName"] = self.get_full_name()
        dictionary["ranking"] = self.ranking.to_dict() if self.ranking else None
        dictionary["categories"] = [category.code for category in self.categories]
        return dictionary

    def get_full_name(self):
        return f"{self.last_name.upper()} {self.first_name.title()}"

    def are_different(self, player):
        return (self.last_name != player.last_name or
                self.first_name != player.first_name or
                self.club != player.club or
                self.ranking_id != player.ranking_id or
                self.phone_number != player.phone_number or
                self.email != player.email)