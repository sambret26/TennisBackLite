from infrastructure.database.models.player import Player
from infrastructure.database.models.player_categories import PlayerCategories
from database import db
from sqlalchemy.exc import IntegrityError, PendingRollbackError

class PlayerRepository:

    @staticmethod
    def get_total_players():
        return Player.query.count()

    @staticmethod
    def get_rankings_ids():
        results = Player.query.with_entities(Player.ranking_id).all()
        return [result[0] for result in results]

    @staticmethod
    def get_rankings_ids_by_category(category_id):
        results = db.session.query(Player.ranking_id).select_from(Player)\
            .join(PlayerCategories, Player.id == PlayerCategories.player_id)\
            .filter(PlayerCategories.category_id == category_id).all()
        return [result[0] for result in results]

    @staticmethod
    def get_players_by_id_map():
        return {p.id : p for p in Player.query.all()}

    @staticmethod
    def get_players_by_crm_id_map():
        return {p.crm_id : p for p in Player.query.all()}

    @staticmethod
    def update_player(player):
        Player.query.filter_by(id=player.id).update(player.to_dict_for_db())
        db.session.commit()

    @staticmethod
    def save_all(players):
        for player in players:
            player.categories = []
        db.session.add_all(players)
        db.session.commit()

    @staticmethod
    def delete_player(player):
        try:
            db.session.delete(player)
            db.session.commit()
            return True
        except (IntegrityError, PendingRollbackError):
            db.session.rollback()
            logger.error(logger.BATCH, f"Error deleting player {player.id}")
            return False

    @staticmethod
    def delete_all():
        Player.query.delete()
        db.session.commit()