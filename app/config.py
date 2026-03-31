# config.py
from pathlib import Path
from platformdirs import user_data_dir

APP_NAME = "FinanList"
APP_AUTHOR = "STASIMAC"
APP_LOGO = "logo.svg"

# Window settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600


DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "finanlist_database.db"

ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"
APP_LOGO_SVG = ICONS_DIR / APP_LOGO
