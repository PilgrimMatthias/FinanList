# main.py
import os, sys, locale
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication
from app.config import DATA_DIR, DB_PATH
from app.database.connection import Database
from app.app import MainWindow
from app.core.theme import ThemeManager


def main():
    # Ustawienie lokalizacji i kodowania znaków
    locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")
    os.environ["LANG"] = "pl_PL.UTF-8"
    os.environ["LC_ALL"] = "pl_PL.UTF-8"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(DB_PATH)
    db = Database(DB_PATH)

    app = QApplication(sys.argv)

    theme = ThemeManager(app)
    theme.apply_theme("light")

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

    window = MainWindow(database=db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
