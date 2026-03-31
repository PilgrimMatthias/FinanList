from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import QByteArray
from pathlib import Path


class LogoWidget(QSvgWidget):
    def __init__(
        self,
        parent=None,
        file: str = None,
        accent_color: str = "#A3CAAB",
        outline_color: str = "#000000",
    ):
        super().__init__(parent)

        svg = Path(file).read_text()
        svg = svg.replace("{{ACCENT_COLOR}}", accent_color)
        svg = svg.replace("{{OUTLINE_COLOR}}", outline_color)

        self.load(QByteArray(svg.encode()))
