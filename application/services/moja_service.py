from infrastructure.database.models.category import Category
from infrastructure.database.models.court import Court
from infrastructure.database.models.grid import Grid
from infrastructure.database.models.match import Match
from infrastructure.database.models.ranking import Ranking
from infrastructure.database.repositories.category_repository import CategoryRepository
from infrastructure.database.repositories.competition_repository import CompetitionRepository
from infrastructure.database.repositories.court_repository import CourtRepository
from infrastructure.database.repositories.grid_repository import GridRepository
from infrastructure.database.repositories.match_repository import MatchRepository
from infrastructure.database.repositories.message_repository import MessageRepository
from infrastructure.database.repositories.player_repository import PlayerRepository
from infrastructure.database.repositories.player_categories_repository import PlayerCategoriesRepository
from infrastructure.database.repositories.ranking_repository import RankingRepository
from infrastructure.database.repositories.setting_repository import SettingRepository
from infrastructure.database.repositories.url_repository import UrlRepository
from infrastructure.external import moja_requests

category_repository = CategoryRepository()
competition_repository = CompetitionRepository()
court_repository = CourtRepository()
grid_repository = GridRepository()
match_repository = MatchRepository()
message_repository = MessageRepository()
player_categories_repository = PlayerCategoriesRepository()
player_repository = PlayerRepository()
ranking_repository = RankingRepository()
setting_repository = SettingRepository()
url_repository = UrlRepository()

def get_players_infos(homologation_id):
    players_url = url_repository.get_url_by_label("Players").replace("HOMOLOGATION_ID", homologation_id)
    return moja_requests.send_get_request(players_url)

def get_teams_infos(homologation_id):
    teams_url = url_repository.get_url_by_label("Teams").replace("HOMOLOGATION_ID", homologation_id)
    return moja_requests.send_get_request(teams_url)

def get_call_ups(category_id):
    call_ups_url = url_repository.get_url_by_label("CallUps").replace("CATEGORY_ID", str(category_id))
    return moja_requests.send_get_request(call_ups_url)

def update_matches():
    ctx = UpdateMatchesContext()
    current_category_id = None
    match_index = 1
    for grid in ctx.grids:
        if current_category_id != grid.category_id:
            match_index = 1
        update_matches_by_grid(ctx, grid, match_index)
        current_category_id = grid.category_id
    for match in ctx.new_matches:
        handle_match(ctx, match)
    if ctx.new_matches:
        match_repository.save_all(ctx.new_matches)
    if ctx.matches_to_save:
        match_repository.save_all(ctx.matches_to_save)
    if ctx.matches_by_id_map:
        match_repository.delete_all_by_id([m.id for m in ctx.matches_by_id_map.values()])
        ctx.deleted += len(ctx.matches_by_id_map)
    # TODO log

def update_courts():
    courts_information = get_court_information()
    if courts_information is not None and courts_information:
        court_repository.delete_all()
        court_repository.add_courts([Court.from_fft(court) for court in courts_information['list']])

def update_categories():
    homologation_id = competition_repository.get_homologation_id()
    categories = moja_requests.send_get_request(url_repository.get_url_by_label("Category")
                                          .replace("HOMOLOGATION_ID", str(homologation_id)))
    if categories is not None and categories:
        grid_repository.delete_all()
        category_repository.delete_all()
        category_repository.add_categories([Category.from_fft(category) for category in categories])

def update_grids():
    for category in category_repository.get_all_categories():
        url = url_repository.get_url_by_label("CategoryData").replace("CATEGORY_ID", str(category.id))
        category_info = moja_requests.send_get_request(url)
        if category_info is None or not category_info:
            return
        grids_to_add = []
        grids = sorted(category_info, key=lambda x: x['decId'])
        for index, grid in enumerated(grids):
            new_grid = Grid.from_fft(grid)
            new_grid.category_id = category.id
            if index != len(grids) -1:
                new_grid.code = category.code + str(index + 1)
            else:
                new_grid.code = "TF" + category.code
            grids_to_add.append(new_grid)
        grid_repository.delete_all_by_category(category.id)
        grid_repository.add_grids(grids_to_add)

def update_rankings():
    rankings = moja_requests.send_get_request(url_repository.get_url_by_label("Rankings"))
    if rankings is not None and rankings:
        player_repository.delete_all()
        ranking_repository.delete_all()
        ranking_repository.add_rankings([Ranking.from_fft(ranking) for ranking in rankings])

def update_matches_by_grid(ctx, grid, match_index):
    if grid.grid_type == "POU":
        return None
    matches = []
    grid_url = url_repository.get_url_by_label("GridData").replace("GRID_ID", str(grid.table_id))
    matches_from_moja = moja_requests.send_get_request(grid_url)
    if matches_from_moja is None:
        return None
    sorted_matchs = sorted(matches_from_moja, key=lambda x: getTuple(x["numeroMatch"]))
    for match in sorted_matchs:
        new_match = create_match(ctx, match, grid, match_index)
        matches.append(new_match)
        match_index += 1
        ctx.temp_matches_map[str(new_match.id)] = new_match.label
    for match in matches:
        match_in_db = ctx.matches_by_id_map.get(match.id)
        if match_in_db:
            if match.are_different(match_in_db):
                ctx.updated += 1
                ctx.matches_to_save.append(match)
            ctx.matches_by_id_map.pop(match.id)
        else:
            ctx.new_matches.append(match)
            ctx.added += 1
    return len(matches)

def create_match(ctx, match, grid, match_index):
    new_match = Match.from_fft(match)
    new_match.category_id = grid.category_id
    new_match.grid_id = grid.id
    new_match.label = grid.category.code + str(match_index).zfill(2)
    set_players_or_teams(ctx, new_match, match)
    set_next_round(new_match, match)
    set_winner(new_match, match)
    set_schedule(new_match, match)
    return new_match

def handle_match(ctx, match):
    if is_real_player(match.future_player1):
        match.future_player1 = ctx.temp_matches_map.get(str(match.future_player1))
    if is_real_player(match.future_player2):
        match.future_player2 = ctx.temp_matches_map.get(str(match.future_player2))
    if match.next_round is not None:
        next_round = ctx.temp_matches_map.get(str(match.next_round))
        if next_round is not None:
            match.next_round = next_round
        else:
            next_grid_id = ctx.next_grid_map.get(match.next_round)
            if next_grid_id is not None:
                match.next_round = ctx.grid_code_by_id_map.get(next_grid_id)
            else:
                match.next_round = None

def set_players_or_teams(ctx, new_match, match):
    prec = 0
    qe = 0
    if match['insId1'] is None:
        if len(match['matchsPrecedents']) > 0:
            new_match.future_player1 = str(match['matchsPrecedents'][0]['matchId'])
            prec += 1
        elif match['haveQe']:
            new_match.future_player1 = "QE"
            qe += 1
    elif new_match.double:
        new_match.team1_id = match['insId1']
    else:
        new_match.player1_id = get_player_id(ctx, match['insId1'])
    if match['insId2'] is None:
        if len(match['matchsPrecedents']) > prec:
            new_match.future_player2 = str(match['matchsPrecedents'][prec]['matchId'])
        elif not qe and match['haveQe']:  # TODO : 2 qe ?
            new_match.future_player2 = "QE"
    elif new_match.double:
        new_match.team2_id = match['insId2']
    else:
        new_match.player2_id = get_player_id(ctx, match['insId2'])

def set_next_round(new_match, match):
    if len(match['matchsSuivants']) > 0:
        new_match.next_round = str(match['matchsSuivants'][0]['matchId'])
    else:
        new_match.next_round = str(match['decoupageId'])

def set_winner(new_match, match):
    if match["insIdWin"] is None:
        return
    new_match.finish = True
    if new_match.double:
        if match["insIdWin"] == match['insId1']:
            new_match.team_winner = new_match.team1_id
        else:
            new_match.team_winner = new_match.team2_id
    else:
        if match["insIdWin"] == match['insId1']:
            new_match.winner_id = new_match.player1_id
        else:
            new_match.winner_id = new_match.player2_id
    set_score(new_match, match)


def set_score(new_match, match):
    score = ""
    for tennis_set in match["sets"]:
        if tennis_set["scoreA"] == 0 and tennis_set["scoreB"] == 0:
            break
        if score != "":
            score += " "
        if match["insIdWin"] == match['insId1']:
            score += str(tennis_set["scoreA"]) + "/" + str(tennis_set["scoreB"])
        else:
            score += str(tennis_set["scoreB"]) + "/" + str(tennis_set["scoreA"])
        if tennis_set["tieBreak"] is not None:
            score += "(" + str(tennis_set["tieBreak"]) + ")"
    new_match.score = score

def set_schedule(new_match, match):
    if match["dateProgrammation"] and "T" in match["dateProgrammation"]:
        new_match.day = match["dateProgrammation"].split("T")[0]
        new_match.hour = match["dateProgrammation"].split("T")[1][:5]

def get_player_id(ctx, inscription_id):
    if inscription_id is None:
        return None
    return ctx.players_by_id_map.get(inscription_id)

def is_real_player(future_player):
    return future_player is not None and future_player != "QE"

def get_court_information():
    homologation_id = competition_repository.get_homologation_id()
    data = {
        "queryInput": {
            "criteria": {
                "date": "2026-01-01T12:00",
                "homologationsChoisiesIdList": [
                    homologation_id
                ]
            }
        }
    }
    return moja_requests.send_post_request_with_headers(url_repository.get_url_by_label("Courts"), data)

class UpdateMatchesContext:
    def __init__(self):
        self.added = 0
        self.updated = 0
        self.deleted = 0
        self.grids = grid_repository.get_all_grids()
        self.matches_by_id_map = match_repository.get_matches_by_id_map()
        self.new_matches = []
        self.temp_matches_map = {}
        self.next_grid_map = grid_repository.get_next_grids_map()
        self.grid_code_by_id_map = grid_repository.get_grid_code_by_id_map()
        self.matches_to_save = []
        self.players_by_id_map = player_categories_repository.get_player_id_by_inscr_id_map()