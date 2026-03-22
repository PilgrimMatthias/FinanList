# config.py
from pathlib import Path
from platformdirs import user_data_dir

APP_NAME = "FinanList"
APP_AUTHOR = "STASIMAC"

DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "finanlist_database.db"
