from infrastructure.database.models.category import Category
from database import db

class CategoryRepository:

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def get_categories_by_id_map():
        return {c.id : c for c in Category.query.all()}

    @staticmethod
    def add_categories(categories):
        db.session.add_all(categories)
        db.session.commit()

    @staticmethod
    def delete_all():
        Category.query.delete()
        db.session.commit()