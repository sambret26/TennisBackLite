from infrastructure.database.models.call_up import CallUp
from database import db

class CallUpRepository:

    @staticmethod
    def get_call_ups_by_id_map():
        return {c.call_up_id: c for c in CallUp.query.all()}

    @staticmethod
    def save_all(call_ups):
        db.session.add_all(call_ups)
        db.session.commit()