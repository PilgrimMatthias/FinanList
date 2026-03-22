# main.py
from app.config import DATA_DIR, DB_PATH
from app.database.connection import Database

DATA_DIR.mkdir(parents=True, exist_ok=True)
db = Database(DB_PATH)
