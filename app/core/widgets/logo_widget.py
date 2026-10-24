from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import QByteArray
from pathlib import Path
from app.core.theme.palette import Palette, palette_signals


class LogoWidget(QSvgWidget):
    def __init__(
        self,
        parent=None,
        file: str = None,
        accent_color: str = "#A3CAAB",
        outline_color: str = None,
    ):
        super().__init__(parent)
        self.file = file
        self._accent_color = accent_color 
        self._outline_color = outline_color or Palette.hex("icon")
        self._load(self._accent_color, self._outline_color)
        palette_signals.changed.connect(self._on_theme_changed)

    def _load(self, accent_color:str, outline_color:str):
        svg = Path(self.file).read_text(encoding="utf-8")
        svg = svg.replace("{{ACCENT_COLOR}}", accent_color)
        svg = svg.replace("{{OUTLINE_COLOR}}", outline_color)

        self.load(QByteArray(svg.encode()))

    def _on_theme_changed(self, theme: str):
        self._outline_color = Palette.hex("icon")
        self._load(self._accent_color, self._outline_color)
