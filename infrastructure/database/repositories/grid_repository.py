from infrastructure.database.models.grid import Grid
from database import db

class GridRepository:

    @staticmethod
    def get_all():
        return Grid.query.order_by(Grid.category_id).order_by(Grid.id).all()

    @staticmethod
    def get_next_grids_map():
        grids = Grid.query.all()
        return {str(grid.id): grid.next_grid_id for grid in grids}

    @staticmethod
    def get_code_by_id_map():
        grids = Grid.query.all()
        return {grid.id: grid.code for grid in grids}

    @staticmethod
    def add_all(grids):
        db.session.add_all(grids)
        db.session.commit()

    @staticmethod
    def delete_all_by_category(category_id):
        Grid.query.filter_by(category_id=category_id).delete()
        db.session.commit()

    @staticmethod
    def delete_all():
        Grid.query.delete()
        db.session.commit()