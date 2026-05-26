from flask import Blueprint, jsonify
from infrastructure.database.repositories.profile_repository import ProfileRepository

profile_repository = ProfileRepository()

profile_bp = Blueprint('profileBp', __name__, url_prefix='/profiles')

@profile_bp.route('/', methods=['GET'])
def get_profiles():
    profiles = profile_repository.get_all_profiles()
    return jsonify([profile.to_dict() for profile in profiles]), 201