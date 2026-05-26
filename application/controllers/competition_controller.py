from flask import Blueprint, jsonify, request

from application.services import competition_service, moja_service
from batchs import registrations_batch
from infrastructure.database.repositories.competition_repository import CompetitionRepository
from infrastructure.database.repositories.setting_repository import SettingRepository


competition_repository = CompetitionRepository()
setting_repository = SettingRepository()

competition_bp = Blueprint('competitionBp', __name__, url_prefix='/competitions')

@competition_bp.route('/', methods=['GET'])
def get_competitions():
    competitions = competition_repository.get_competitions()
    return jsonify([competition.to_dict() for competition in competitions]), 200

@competition_bp.route('/update', methods=['POST'])
def update_competitions():
    result = competition_service.update_competitions()
    if result is None:
        return jsonify({'message': 'No competitions found!'}), 404
    return jsonify({'message': 'Competitions updated successfully!'}), 200

@competition_bp.route('/dates', methods=['GET'])
def get_dates():
    dates =  competition_repository.get_dates()
    if dates is None or dates == (None, None):
        return jsonify({'message': 'No competitions found!'}), 404
    return jsonify({'startDate': dates[0], 'endDate': dates[1]}), 200

@competition_bp.route('/active', methods=['PUT'])
def active_competition():
    is_batch_active = setting_repository.get_batchs_active()
    if is_batch_active:
        setting_repository.set_batchs_active("0")
    competition_id = request.json['competitionId']
    competition_repository.set_inactive()
    competition_repository.set_active(competition_id)
    return jsonify({'message': 'Competition updated successfully!', 'isBatchActive': is_batch_active}), 200

@competition_bp.route('/deleteAllDatas', methods=['DELETE'])
def delete_datas():
    competition_service.delete_datas()
    return jsonify({'message': 'Data deleted successfully!'}), 200

@competition_bp.route('/courts', methods=['POST'])
def update_courts():
    moja_service.update_courts()
    return jsonify({'message': 'Courts updated successfully!'}), 200

@competition_bp.route('/categories', methods=['POST'])
def update_categories():
    moja_service.update_categories()
    return jsonify({'message': 'Categories updated successfully!'}), 200

@competition_bp.route('/grids', methods=['POST'])
def update_grids():
    moja_service.update_grids()
    return jsonify({'message': 'Grids updated successfully!'}), 200

@competition_bp.route('/matches', methods=['POST'])
def update_matches():
    moja_service.update_matches()
    return jsonify({'message': 'Matches updated successfully!'}), 200

@competition_bp.route('/rankings', methods=['POST'])
def update_rankings():
    moja_service.update_rankings()
    return jsonify({'message': 'Rankings updated successfully!'}), 200

@competition_bp.route('/players', methods=['POST'])
def update_players():
    registrations_batch.run(False)
    return jsonify({'message': 'Players updated successfully!'}), 200