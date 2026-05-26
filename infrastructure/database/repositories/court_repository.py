from infrastructure.database.models.court import Court
from database import db

class CourtRepository:

    @staticmethod
    def add_courts(courts):
        db.session.add_all(courts)
        db.session.commit()

    @staticmethod
    def delete_all():
        Court.query.delete()
        db.session.commit()