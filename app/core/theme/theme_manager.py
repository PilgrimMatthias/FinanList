from pathlib import Path
from PySide6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self, app: QApplication):
        self.app = app

    def apply_theme(self, theme_name: str = "dark"):
        theme_path = Path(__file__).parent / f"{theme_name}.qss"
        with open(theme_path) as f:
            self.app.setStyleSheet(f.read())
