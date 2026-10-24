# main.py
import os, sys, locale
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication
from app.config import DATA_DIR, DB_PATH
from app.database.connection import Database
from app.app import MainWindow
from app.core.theme import ThemeManager
from app.core.app_state import AppState
from app.features.settings import SettingsService


def main():
    # Ustawienie lokalizacji i kodowania znaków
    try:
        locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_ALL, "")    # system default
    os.environ["LANG"] = "pl_PL.UTF-8"
    os.environ["LC_ALL"] = "pl_PL.UTF-8"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(DB_PATH)

    app = QApplication(sys.argv)

    db = Database(DB_PATH)
    app_state = AppState()
    settings_service = SettingsService(app_state=app_state)

    theme = ThemeManager(app)
    app_state.theme_changed.connect(theme.apply_theme)

    QDir.addSearchPath(
        "images",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images"),
    )
    QDir.addSearchPath(
        "icons",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons"),
    )
    QDir.addSearchPath(
        "svg",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "svg"),
    )
    theme.apply_theme(settings_service.get_theme())

    window = MainWindow(database=db, app_state=app_state, settings_service=settings_service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
