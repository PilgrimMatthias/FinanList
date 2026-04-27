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
IMAGES_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
SVG_DIR = Path(__file__).resolve().parent.parent / "assets" / "svg"
APP_LOGO_SVG = ICONS_DIR / APP_LOGO
DOWN_ARROW_ICON = SVG_DIR / "down_arrow.svg"
RIGHT_ARROW_ICON = SVG_DIR / "right_arrow.svg"

# New transaction window
TRANSACTION_WINDOW_WIDTH = 500
TRANSACTION_WINDOW_HEIGHT = 715

# New/Edit category window
CATEGORY_WINDOW_WIDTH = 350
CATEGORY_WINDOW_HEIGHT = 465
