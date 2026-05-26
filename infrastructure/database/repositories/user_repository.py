from sqlalchemy import func, or_
from database import db
from infrastructure.database.models.users import User

class UserRepository:

    @staticmethod
    def get_all_users():
        return User.query.order_by(User.profile.desc()).all()

    @staticmethod
    def get_user_by_name(name):
        return User.query.filter(func.lower(User.name) == name.lower()).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_admin_with_password(password):
        return User.query.filter(User.password==password,
                                 or_(User.profile==2, User.super_admin==1)).first()

    @staticmethod
    def add_user(user):
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_profile(user_id, new_role, super_admin):
        User.query.filter_by(id=user_id).update({"profile": new_role, "super_admin": super_admin})
        db.session.commit()
        user = User.query.filter_by(id=user_id).first()
        return user

    @staticmethod
    def update_password(user_id, password):
        User.query.filter_by(id=user_id).update({"password": password})
        db.session.commit()