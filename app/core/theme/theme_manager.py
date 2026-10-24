from pathlib import Path
from PySide6.QtWidgets import QApplication
from .palette import Palette


class ThemeManager:
    """
    Theme Manager - aplies theme and color palette
    """
    def __init__(self, app: QApplication):
        self.app = app

    def apply_theme(self, theme_name: str = "light"):
        qss = self._load_qss(theme_name=theme_name)
        Palette.set_theme(theme=theme_name)
        self.app.setStyleSheet(qss)

    def _load_qss(self, theme_name:str = "light"):
        theme_path = Path(__file__).parent / f"{theme_name}.qss"

        return theme_path.read_text(encoding="utf-8")
 