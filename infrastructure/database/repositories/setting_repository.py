from infrastructure.database.models.setting import Setting
from database import db

class SettingRepository:

    @staticmethod
    def get_all_settings():
        return Setting.query.all()

    @staticmethod
    def get_setting_by_id(setting_id: int):
        return Setting.query.get(setting_id)

    @staticmethod
    def get_batchs_active():
        return Setting.query.filter(Setting.key == 'batchs_active').first().value == "1"

    @staticmethod
    def get_refresh_token():
        return Setting.query.filter(Setting.key == 'refresh_token').first().value

    @staticmethod
    def get_auth_error():
        return Setting.query.filter(Setting.key == 'auth_error').first().value == "1"

    @staticmethod
    def set_batchs_active(batchs_active):
        Setting.query.filter(Setting.key == 'batchs_active').update({Setting.value: batchs_active})
        db.session.commit()

    @staticmethod
    def set_auth_error(auth_error):
        Setting.query.filter(Setting.key == 'auth_error').update({Setting.value: auth_error})
        db.session.commit()

    @staticmethod
    def set_refresh_token(refresh_token):
        Setting.query.filter(Setting.key == 'refresh_token').update({Setting.value: refresh_token})
        db.session.commit()