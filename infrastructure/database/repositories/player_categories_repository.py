from infrastructure.database.models import player_categories
from infrastructure.database.models.player_categories import PlayerCategories
from database import db

class PlayerCategoriesRepository:

    @staticmethod
    def get_player_number_by_category(category_id):
        return PlayerCategories.query.filter_by(category_id=category_id).count()

    @staticmethod
    def get_player_id_by_inscr_id_map():
        return {player_category.id: player_category.player_id for player_category in PlayerCategories.query.all()}

    @staticmethod
    def save_all(player_categories):
        db.session.add_all(player_categories)
        db.session.commit()

    @staticmethod
    def delete_all(player_categories):
        db.session.delete_all(player_categories)
        db.session.commit()

    @staticmethod
    def delete_all():
        PlayerCategories.query.delete()
        db.session.commit()