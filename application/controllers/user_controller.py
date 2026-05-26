import jwt
from flask import Blueprint, jsonify, request
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.message_repository import MessageRepository
from infrastructure.database.repositories.profile_repository import ProfileRepository
from infrastructure.database.models.users import User
from infrastructure.database.models.message import Message
from config import Config
from common.constants import constants

SECRET_KEY = Config.SECRET_KEY

user_repository = UserRepository()
message_repository = MessageRepository()
profile_repository = ProfileRepository()

user_bp = Blueprint('userBp', __name__, url_prefix='/users')

@user_bp.route('/connect', methods=['POST'])
def connect_user():
    data = request.json
    user = user_repository.get_user_by_name(data['username'])
    if not user:
        return jsonify({'message': constants.USER_NOT_FOUND}), 404
    if user.password != data['password']:
        return jsonify({'message': constants.WRONG_PASSWORD}), 401
    token = jwt.encode(user.toDict(), SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token}), 200

@user_bp.route('/create', methods=['POST'])
def create_account():
    data = request.json
    user = user_repository.get_user_by_name(data['username'])
    if user:
        return jsonify({'message': constants.USER_ALREADY_EXISTS}), 409
    user = User.from_json(data)
    user_repository.add_user(user)
    message = Message("USERS", f"{user.name.title()} a crée son compte")
    message_repository.add_message(message)
    token = jwt.encode(user.toDict(), SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token}), 200

@user_bp.route('/<int:userId>/role', methods=['PUT'])
def update_role(user_id):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': constants.USER_NOT_FOUND}), 404
    new_role = int(request.json['newRole'])
    if new_role < user.profileValue or user.superAdmin == 1:
        if user.profileValue == 2:
            user = user_repository.update_profile(user_id, new_role, 1)
        else :
            user = user_repository.update_profile(user_id, new_role, user.superAdmin)
        token = jwt.encode(user.toDict(), SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'message': constants.CANNOT_CHANGE_ROLE}), 403

@user_bp.route('/admin/connect', methods=['POST'])
def connect_admin():
    data = request.json
    password = data['password']
    user_id = int(data['userId'])
    new_role = int(data['newRole'])
    admin = user_repository.get_admin_with_password(password)
    if not admin:
        return jsonify({'message': constants.INVALID_PASSWORD}), 401
    user = user_repository.update_profile(user_id, new_role, 0)
    token = jwt.encode(user.toDict(), SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token}), 200

@user_bp.route('/<int:userId>/access', methods=['POST'])
def ask_access(user_id):
    data = request.json
    role = str(data['role'])
    user = user_repository.get_user_by_id(user_id)
    profile = profile_repository.get_profile_by_value(role)
    if not user or not profile:
        return jsonify({'message': constants.USER_NOT_FOUND}), 404
    message = Message("ASK", f"{user.name.title()} a demandé des accès {profile.label}")
    message_repository.add_message(message)
    return jsonify({'message': 'Message sent!'}), 200

@user_bp.route('/<int:userId>/changePassword', methods=['PUT'])
def change_password(user_id):
    data = request.json
    old_password = str(data['oldPassword'])
    password = str(data['password'])
    user = user_repository.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': constants.USER_NOT_FOUND}), 404
    if user.password != old_password:
        return jsonify({'message': constants.INVALID_PASSWORD}), 401
    user.password = password
    user_repository.update_password(user_id, password)
    return jsonify({'message': constants.PASSWORD_CHANGED}), 200

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = user_repository.get_all_users()
    return jsonify([user.toDict() for user in users]), 200

@user_bp.route('/update', methods=['PUT'])
def update_users():
    users = request.json['users']
    for user_id, user_profile in users.items():
        user_repository.update_profile(user_id, user_profile, 0)
    return jsonify({'message': constants.USERS_UPDATED}), 200