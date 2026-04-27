from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QPushButton
from pathlib import Path

from app.config import DOWN_ARROW_ICON, RIGHT_ARROW_ICON


class ExpandToggleButton(QPushButton):
    def __init__(
        self, color: str = "#cdd6f4", size: int = 16, on_click=None, parent=None
    ):
        super().__init__(parent)
        self.setFixedSize(
            size + 8, size + 8
        )  # button slightly bigger than icon for hover padding
        self._icon_size = size
        self._color = color
        self._expanded = False

        self._down_icon = self._load_icon(DOWN_ARROW_ICON)
        self._right_icon = self._load_icon(RIGHT_ARROW_ICON)

        if on_click:
            self.clicked.connect(on_click)

        self.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            "QPushButton:hover { background: #4a4a4a; border-radius: 4px; }"
        )
        self._update_icon()

    def _load_icon(self, path: Path) -> QIcon:
        """Load SVG, replace color placeholder, render to QIcon."""
        svg_text = Path(path).read_text()
        svg_text = svg_text.replace("{{ICON_COLOR}}", self._color)

        renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
        pixmap = QPixmap(self._icon_size, self._icon_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def set_expanded(self, expanded: bool):
        self._expanded = expanded
        self._update_icon()

    def toggle(self) -> bool:
        self.set_expanded(not self._expanded)
        return self._expanded

    def is_expanded(self) -> bool:
        return self._expanded

    def _update_icon(self):
        self.setIcon(self._down_icon if self._expanded else self._right_icon)
        self.setIconSize(self.size())
