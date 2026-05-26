from flask import Blueprint, jsonify, request
from infrastructure.database.repositories.setting_repository import SettingRepository

setting_repository = SettingRepository()

setting_bp = Blueprint('settingBp', __name__, url_prefix='/settings')

@setting_bp.route('/', methods=['GET'])
def get_settings():
    settings = setting_repository.get_all_settings()
    settings_dict = {setting.key: setting.value for setting in settings}
    return jsonify(settings_dict), 200

@setting_bp.route('/batchsActive', methods=['PUT'])
def set_batchs_active():
    batchs_active = request.json['batchsActive']
    setting_repository.set_batchs_active(batchs_active)
    return jsonify({'message': 'Batchs active updated successfully!'}), 200

@setting_bp.route('/token', methods=['PUT'])
def update_token():
    token = request.json['token']
    setting_repository.set_refresh_token(token)
    return jsonify({'message': 'Token updated successfully!'}), 200
