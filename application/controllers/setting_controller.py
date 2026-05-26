from flask import Blueprint, jsonify, request
from infrastructure.database.repositories.setting_repository import SettingRepository

setting_repository = SettingRepository()

setting_bp = Blueprint('settingBp', __name__, url_prefix='/settings')

@setting_bp.route('/batchsActive', methods=['GET'])
def get_batchs_active():
    batchs_active = setting_repository.get_batchs_active() == 1
    return jsonify({'batchs_active': batchs_active}), 200

@setting_bp.route('/batchsActive', methods=['PUT'])
def set_batchs_active():
    batchs_active = request.json['batchsActive']
    setting_repository.set_batchs_active(batchs_active)
    return jsonify({'message': 'Batchs active updated successfully!'}), 200

@setting_bp.route('/token', methods=['PUT'])
def update_token():
    token = request.json['token']
    setting_repository.set_refresh_token(token)
    setting_repository.set_auth_error(0)
    return jsonify({'message': 'Token updated successfully!'}), 200
