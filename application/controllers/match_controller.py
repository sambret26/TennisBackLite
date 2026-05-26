from flask import Blueprint, jsonify, request

from infrastructure.database.repositories.match_repository import MatchRepository
from infrastructure.database.repositories.setting_repository import SettingRepository
from infrastructure.logger.logger import log

match_repository = MatchRepository()
setting_repository = SettingRepository()

match_bp = Blueprint('matchBp', __name__, url_prefix='/matches')

@match_bp.route('/planning', methods=['GET'])
def get_matches_for_planning():
    date = request.args.get('date')
    matches = match_repository.get_matches_for_planning(date)
    return jsonify([match.to_dict() for match in matches]), 200

@match_bp.route('/result', methods=['POST'])
def update_match_result():
    data = request.json
    match_id = data['matchId']
    winner_id = data['playerId']
    score = data['score']
    finish = data['finish']
    double = data['double']
    match = match_repository.get_match_by_id(match_id)
    status = 200
    if not match:
        return jsonify({'message': 'Match not found!'}), 404
    if double :
        match.team_winner_id = winner_id
    else :
        match.winner_id = winner_id
    match.score = score
    match.finish = finish
    match_repository.update_match(match)
    #TODO : doubles
    winner_team = ""
    if winnerId == match.player1_id:
        winner_team = "equipeA"
    elif winnerId == match.player2_id:
        winner_team = "equipeB"
    if winner_team == "":
        log.error("Result", "Le vainqueur n'est pas connu")
    return jsonify({'message': 'Match result updated successfully!'}), status