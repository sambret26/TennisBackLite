from infrastructure.database.models.match import Match
from database import db

class MatchRepository:

    @staticmethod
    def get_by_id(match_id):
        return Match.query.get(match_id)

    @staticmethod
    def get_by_label(match_label):
        return Match.query.filter(Match.label == match_label).first()

    @staticmethod
    def get_all_by_date(date):
        return Match.query.filter(Match.day == date).order_by(Match.hour, Match.court_id.asc()).all()

    @staticmethod
    def get_by_id_map():
        return {m.id: m for m in Match.query.all()}

    @staticmethod
    def get_for_planning(date):
        return Match.query.filter(Match.day == date).order_by(Match.hour, Match.court_id.asc()).all()

    @staticmethod
    def update(match):
        db.session.merge(match)
        db.session.commit()

    @staticmethod
    def update_all(matches):
        for match in matches:
            db.session.merge(match)
        db.session.commit()

    @staticmethod
    def save_all(matches):
        db.session.add_all(matches)
        db.session.commit()

    @staticmethod
    def delete_all_by_ids(match_ids):
        Match.query.filter(Match.id.in_(match_ids)).delete()
        db.session.commit()

    @staticmethod
    def delete_all():
        Match.query.delete()
        db.session.commit()
