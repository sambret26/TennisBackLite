from infrastructure.database.models.competition import Competition
from database import db

class CompetitionRepository:

    @staticmethod
    def get_competitions():
        return Competition.query.order_by(Competition.label).all()

    @staticmethod
    def get_homologation_id():
        competition = Competition.query.filter(Competition.active == True).first()
        if competition is None:
            return None
        return competition.id

    @staticmethod
    def get_dates():
        competition = Competition.query.filter(Competition.active == True).first()
        if competition is None:
            return None
        return competition.start_date, competition.end_date

    @staticmethod
    def add_competitions(competitions):
        db.session.add_all(competitions)
        db.session.commit()

    @staticmethod
    def set_active(competition_id):
        Competition.query.filter_by(id=competition_id).update({Competition.active: 1})
        db.session.commit()

    @staticmethod
    def set_inactive():
        Competition.query.filter_by(active=True).update({Competition.active: 0})
        db.session.commit()

    @staticmethod
    def update_competition(competition_id, competition):
        Competition.query.filter_by(id=competition_id).update(competition.to_dict_for_db())
        db.session.commit()

    @staticmethod
    def delete_competitions(competitions_id):
        Competition.query.filter(Competition.id.in_(competitions_id)).delete()
        db.session.commit()
