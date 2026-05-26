from infrastructure.database.models.team import Team
from database import db

class TeamRepository:

    @staticmethod
    def get_all_ids():
        return [t.id for t in Team.query.all()]

    @staticmethod
    def save_all(teams):
        db.session.add_all(teams)
        db.session.commit()

    @staticmethod
    def delete_all(ids):
        Team.query.filter(Team.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def delete_all():
        Team.query.delete()
        db.session.commit()