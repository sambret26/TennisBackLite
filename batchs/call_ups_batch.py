from application.services import moja_service
from application.services.moja_service import message_repository
from infrastructure.database.models.call_up import CallUp
from infrastructure.database.repositories.call_up_repository import CallUpRepository
from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.match_repository import MatchRepository
from infrastructure.database.repositories.player_repository import PlayerRepository

call_up_repository = CallUpRepository()
category_repository = CategoryRepository()
match_repository = MatchRepository()
player_repository = PlayerRepository()

def run():
    ctx = CallUpsBatchContext()
    for categorie in ctx.categories:
        handle_categorie(ctx, categorie)
    call_up_repository.save_all(ctx.call_ups_to_save)
    message_repository.save_all(ctx.messages)

def handle_categorie(ctx, categorie):
    moja_call_ups = moja_service.get_call_ups(categorie.id)
    for moja_call_up in moja_call_ups:
        call_up = CallUp.from_fft(moja_call_up)
        call_up_in_db = ctx.call_ups_by_id_map.get(call_up.call_up_id)
        if call_up_in_db is None:
            create_call_up(ctx, call_up)
        elif call_up_in_db.state != call_up.state:
            update_call_up(ctx, call_up, call_up_in_db)

def create_call_up(ctx, call_up):
    if call_up.crm_id is None:
        return
    ctx.call_ups_to_save.append(call_up)
    if call_up.state == "ACPT":
        handle_accepted(ctx, call_up)
    elif call_up.state == "NCFR":
        handle_send(ctx, call_up)

def update_call_up(ctx, call_up, call_up_in_db):
    call_up_in_db.state = call_up.state
    ctx.call_ups_to_save.append(call_up_in_db)
    if call_up.crm_id is None:
        return
    if call_up.state == "ACPT":
        handle_accepted(ctx, call_up_in_db)
    elif call_up.state == "NCFR":
        handle_send(ctx, call_up_in_db)

def handle_accepted(ctx, call_up_in_db):
    player_name = ctx.players_by_crm_id_map.get(call_up_in_db.crm_id).get_full_name()
    match = ctx.matches_by_id_map.get(call_up_in_db.match_id)
    if match:
        date = match.get_formatted_date()
        hour = match.get_formatted_hour()
        message = Message("CONVO", f"{player_name} a accepté sa convocation pour le match {match.label} le {date} à {hour}")
    else :
        message = Message("CONVO", f"{player_name} a accepté sa convocation pour un match non identifié")
    ctx.messages.append(message)

def handle_send(ctx, call_up_in_db):
    player_name = ctx.players_by_crm_id_map.get(call_up_in_db.crm_id).get_full_name()
    match = ctx.matches_by_id_map.get(call_up_in_db.match_id)
    if match:
        date = match.get_formatted_date()
        hour = match.get_formatted_hour()
        message = Message("SEND_CONVO", f"{player_name} a été convoqué pour le match {match.label} le {date} à {hour}")
    else :
        message = Message("SEND_CONVO", f"{player_name} a été convoqué pour un match non identifié")
    ctx.messages.append(message)

class CallUpsBatchContext:
    def __init__(self):
        self.categories = category_repository.get_all_categories()
        self.players_by_crm_id_map = player_repository.get_players_by_crm_id_map()
        self.matches_by_id_map = match_repository.get_matches_by_id_map()
        self.call_ups_by_id_map = call_up_repository.get_call_ups_by_id_map()
        self.call_ups_to_save = []
        self.messages = []