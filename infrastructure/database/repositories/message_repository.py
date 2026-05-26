from infrastructure.database.models.message import Message
from database import db

class MessageRepository:

    @staticmethod
    def get_all_messages():
        return Message.query.all()

    @staticmethod
    def get_messages_by_category(category):
        return Message.query.filter(Message.category == category).all()

    @staticmethod
    def delete_messages_by_id(ids):
        Message.query.filter(Message.id.in_(ids)).delete()
        db.session.commit()

    @staticmethod
    def delete_messages_by_category(category):
        Message.query.filter(Message.category == category).delete()
        db.session.commit()

    @staticmethod
    def save(message):
        db.session.add(message)
        db.session.commit()

    @staticmethod
    def save_all(messages):
        db.session.add_all(messages)
        db.session.commit()