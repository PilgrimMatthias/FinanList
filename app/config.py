# config.py
from pathlib import Path
from platformdirs import user_data_dir

APP_NAME = "FinanList"
APP_AUTHOR = "STASIMAC"
APP_LOGO = "logo.svg"

# Window settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600


DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "finanlist_database.db"

ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"
IMAGES_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
SVG_DIR = Path(__file__).resolve().parent.parent / "assets" / "svg"
APP_LOGO_SVG = ICONS_DIR / APP_LOGO
DOWN_ARROW_ICON = SVG_DIR / "down_arrow.svg"
RIGHT_ARROW_ICON = SVG_DIR / "right_arrow.svg"
SEARCH_ICON = SVG_DIR / "search_icon.svg"
EMPTY_TRANSACTIONS = SVG_DIR / "empty_transactions.svg"
EMPTY_BOX = SVG_DIR / "empty_box.svg"

# New transaction window
TRANSACTION_WINDOW_WIDTH = 500
TRANSACTION_WINDOW_HEIGHT = 715

# New/Edit category window
CATEGORY_WINDOW_WIDTH = 350
CATEGORY_WINDOW_HEIGHT = 465

# Wallet window
WALLET_WINDOW_WIDTH = 450
WALLET_WINDOW_HEIGHT = 600

# New/Edit wallet form
WALLET_DIALOG_WIDTH = 350
WALLET_DIALOG_HEIGHT = 325
