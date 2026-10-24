# core/widgets/svg_icon.py
from pathlib import Path
from PySide6.QtCore import QByteArray
from PySide6.QtSvgWidgets import QSvgWidget
from app.core.theme.palette import Palette, palette_signals


class SvgIcon(QSvgWidget):
    """Single-color SVG icon with runtime recoloring."""

    def __init__(self, parent=None, file: str = None, color: str = None):
        super().__init__(parent)
        self._file = file
        self._color = color or Palette.hex("icon")
        self._load()
        palette_signals.changed.connect(self._on_theme_changed)

    def _load(self):
        svg = Path(self._file).read_text(encoding="utf-8")
        svg = svg.replace("{{ICON_COLOR}}", self._color)
        self.load(QByteArray(svg.encode()))

    def set_color(self, color: str):
        self._color = color
        self._load()

    def _on_theme_changed(self, theme: str):
        self.set_color(Palette.hex("icon"))
