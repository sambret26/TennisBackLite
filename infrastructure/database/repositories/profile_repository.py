from infrastructure.database.models.profile import Profile

class ProfileRepository:

    #GETTERS
    @staticmethod
    def get_all_profiles():
        return Profile.query.all()

    @staticmethod
    def get_profile_by_value(value):
        return Profile.query.filter_by(value=value).first()