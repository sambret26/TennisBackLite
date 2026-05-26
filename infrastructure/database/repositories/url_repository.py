from infrastructure.database.models.url import Url

class UrlRepository:

    @staticmethod
    def get_url_by_label(label):
        url = Url.query.filter_by(label=label).first()
        if url is None:
            return None
        return url.url