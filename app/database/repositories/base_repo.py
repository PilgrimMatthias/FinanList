from ..connection import Database


class BaseRepo:
    def __init__(self, db: Database):
        self.db = db
