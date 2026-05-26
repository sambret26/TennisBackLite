from infrastructure.database.models.ranking import Ranking
from database import db

class RankingRepository:

    @staticmethod
    def get_all():
        return Ranking.query.all()

    @staticmethod
    def get_by_id_map():
        return {r.id: r for r in Ranking.query.all()}

    @staticmethod
    def add_all(rankings):
        db.session.add_all(rankings)
        db.session.commit()

    @staticmethod
    def delete_all():
        Ranking.query.delete()
        db.session.commit()
