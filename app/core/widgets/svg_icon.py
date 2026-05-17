# core/widgets/svg_icon.py
from pathlib import Path
from PySide6.QtCore import QByteArray
from PySide6.QtSvgWidgets import QSvgWidget


class SvgIcon(QSvgWidget):
    """Single-color SVG icon with runtime recoloring."""

    def __init__(self, parent=None, file: str = None, color: str = "#000000"):
        super().__init__(parent)
        self._file = file
        self._color = color
        self._load()

    def _load(self):
        svg = Path(self._file).read_text()
        svg = svg.replace("{{ICON_COLOR}}", self._color)
        self.load(QByteArray(svg.encode()))

    def set_color(self, color: str):
        self._color = color
        self._load()
