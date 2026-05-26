from application.services import moja_service
from infrastructure.database.models.message import Message
from infrastructure.database.models.player import Player
from infrastructure.database.models.player_categories import PlayerCategories
from infrastructure.database.models.team import Team
from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.competition_repository import CompetitionRepository
from infrastructure.database.repositories.message_repository import MessageRepository
from infrastructure.database.repositories.player_categories_repository import PlayerCategoriesRepository
from infrastructure.database.repositories.player_repository import PlayerRepository
from infrastructure.database.repositories.ranking_repository import RankingRepository
from infrastructure.database.repositories.team_repository import TeamRepository

category_repository = CategoryRepository()
competition_repository = CompetitionRepository()
message_repository = MessageRepository()
player_categories_repository = PlayerCategoriesRepository()
player_repository = PlayerRepository()
ranking_repository = RankingRepository()
team_repository = TeamRepository()

def run(send_notifications):
    ctx = RegistrationBatchContext(send_notifications)
    handle_players(ctx)
    handle_teams(ctx)

def handle_players(ctx):
    players_from_moja = moja_service.get_players_infos(ctx.homologation_id)
    if not players_from_moja:
        return
    for player in players_from_moja:
        handle_player(ctx, player)
    for player in ctx.players_by_id_map.values():
        delete_player(ctx, player)
    if ctx.players_to_save:
        player_repository.save_all(ctx.players_to_save)
    if ctx.players_categories_to_save:
        player_categories_repository.save_all(ctx.players_categories_to_save)
    if ctx.players_categories_to_delete:
        player_categories_repository.delete_all(ctx.players_categories_to_delete)
    if ctx.send_notifications and ctx.messages:
        message_repository.save_all(ctx.messages)

def handle_teams(ctx):
    teams_from_moja = moja_service.get_teams_infos(ctx.homologation_id)
    teams_ids_in_db = team_repository.get_all_ids()
    teams_to_save = []
    if not teams_from_moja:
        return
    for team_from_moja in teams_from_moja:
        team = Team.from_fft(team_from_moja)
        if team.id in teams_ids_in_db:
            teams_ids_in_db.remove(team.id)
        else:
            teams_to_save.append(team)
    if teams_to_save:
        team_repository.save_all(teams_to_save)
    if teams_ids_in_db:
        team_repository.delete_all(teams_ids_in_db)


def handle_player(ctx, player_from_moja):
    player = Player.from_fft(player_from_moja)
    add_categories_to_player(ctx, player, player_from_moja)
    add_ranking_to_player(ctx, player)
    player_in_db = ctx.players_by_id_map.get(player.id)
    if player_in_db:
        handle_player_categories(ctx, player, player_in_db)
        if player.are_different(player_in_db):
            if player.ranking_id != player_in_db.ranking_id:
                generate_new_ranking_message(ctx, player, player_in_db)
            player_repository.update_player(player)
        ctx.players_by_id_map.pop(player.id)
    else :
        generate_new_player_message(ctx, player)
        ctx.players_to_save.append(player)

def add_categories_to_player(ctx, player, player_from_moja):
    for category in player_from_moja['epreuves']:
        if category['statutInscriptionCode'] != "PAR":
            continue
        category_in_db = ctx.categories_by_id_map.get(category['eprId'])
        player.categories.append(category_in_db)

def add_ranking_to_player(ctx, player):
    if player.ranking_id:
        player.ranking = ctx.ranking_by_id_map.get(player.ranking_id)

def handle_player_categories(ctx, player, player_in_db):
    handle_new_categories(ctx, player, player_in_db)
    handle_old_categories(ctx, player, player_in_db)

def handle_new_categories(ctx, player, player_in_db):
    for category in player.categories:
        if category not in player_in_db.categories:
            ctx.players_categories_to_save.append(PlayerCategories(player.id, category.id))
            msg = generate_registration_message(player)
            ctx.messages.append(Message(category.code, msg))

def handle_old_categories(ctx, player, player_in_db):
    for category in player_in_db.categories:
        if category not in player_in_db.categories:
            ctx.players_categories_to_delete.append(PlayerCategories(player.id, category.id))
            msg = generate_unregistration_message(player)
            ctx.messages.append(Message(category.code, msg))

def delete_player(ctx, player):
    if player_repository.delete_player(player):
        generate_player_unregistration_message(ctx, player)
    else:
        player.to_delete = True
        player_repository.update_player(player)
        generate_failed_unregistration_message(ctx, player)

def generate_new_player_message(ctx, player):
    msg = generate_registration_message(player)
    ctx.messages.append(Message("G", msg))
    for category in player.categories:
        ctx.players_categories_to_save.append(PlayerCategories(player.id, category.id))
        ctx.messages.append(Message(category.code, msg))

def generate_player_unregistration_message(ctx, player):
    msg = generate_unregistration_message(player)
    ctx.messages.append(Message("G", msg))
    for category in player.categories:
        ctx.messages.append(Message(category.code, msg))

def generate_new_ranking_message(ctx, player, player_in_db):
    msg = f"Reclassement de {player.get_full_name()} ({player_in_db.ranking.simple} => {player.ranking.simple})"
    ctx.messages.append(Message("G", msg))

def generate_failed_unregistration_message(ctx, player):
    msg = f"Tentative de suppression de {player.get_full_name()} ({player.club})"
    if player.ranking:
        msg += f" classé(e) {player.ranking.simple}"
    msg += " échouée"
    ctx.messages.append(Message("ERROR", msg))

def generate_registration_message(player):
    msg = f"Nouvelle inscription : {player.get_full_name()} ({player.club})"
    if player.ranking:
        msg += f" classé(e) {player.ranking.simple}"
    return msg

def generate_unregistration_message(player):
    msg = f"Désinscription de {player.get_full_name()} ({player.club})"
    if player.ranking:
        msg += f" classé(e) {player.ranking.simple}"
    return msg

class RegistrationBatchContext:
    def __init__(self, send_notifications):
        self.send_notifications = send_notifications
        self.categories_by_id_map = category_repository.get_categories_by_id_map()
        self.players_by_id_map = player_repository.get_players_by_id_map()
        self.ranking_by_id_map = ranking_repository.get_ranking_by_id_map()
        self.messages = []
        self.players_to_save = []
        self.players_categories_to_save = []
        self.players_categories_to_delete = []
        self.homologation_id = str(competition_repository.get_homologation_id())

