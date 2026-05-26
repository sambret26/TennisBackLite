from infrastructure.database.models.competition import Competition
from infrastructure.database.repositories.competition_repository import CompetitionRepository
from infrastructure.database.repositories.match_repository import MatchRepository
from infrastructure.database.repositories.player_categories_repository import PlayerCategoriesRepository
from infrastructure.database.repositories.player_repository import PlayerRepository
from infrastructure.database.repositories.team_repository import TeamRepository
from infrastructure.database.repositories.url_repository import UrlRepository
from infrastructure.external import moja_requests

competition_repository = CompetitionRepository()
player_categories_repository = PlayerCategoriesRepository()
match_repository = MatchRepository()
player_repository = PlayerRepository()
team_repository = TeamRepository()
url_repository = UrlRepository()

def update_competitions():
    competitions = moja_requests.send_get_request(url_repository.get_url_by_label("Competition"))
    if competitions is None:
        return None
    competitions_in_db = competition_repository.get_competitions()
    competitions_id_to_delete = [competition.id for competition in competitions_in_db]
    competitions_to_add = []
    for competition_fft in competitions:
        competition = Competition.from_fft(competition_fft)
        competition_in_db = next((comp for comp in competitions_in_db if comp.id == competition.id), None)
        if competition_in_db:
            if competition.are_different(competition_in_db):
                competition_repository.update_competition(competition_in_db.id, competition)
            competitions_id_to_delete.remove(competition.id)
        else:
            competitions_to_add.append(competition)
    competition_repository.add_competitions(competitions_to_add)
    competition_repository.delete_competitions(competitions_id_to_delete)
    return 200

def delete_datas():
    player_categories_repository.delete_all()
    match_repository.delete_all()
    team_repository.delete_all()
    player_repository.delete_all()