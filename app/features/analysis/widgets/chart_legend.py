from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from app.core.theme.palette import Palette, palette_signals

SQUARE = "square"
DASHED_SQUARE = "dashed_square"
LINE = "line"
DASHED_LINE = "dashed_line"

SWATCH_SQUARE = 10
SWATCH_LINE = 16


class LegendSwatch(QWidget):
    """The little mark in front of a legend label."""

    def __init__(self, parent=None, color_key: str = None, kind: str = SQUARE):
        super().__init__(parent)
        self.color_key = color_key
        self.kind = kind

        width = SWATCH_LINE if kind in (LINE, DASHED_LINE) else SWATCH_SQUARE
        self.setFixedSize(QSize(width, SWATCH_SQUARE))

        # A bound method, not a lambda: Qt drops it when the swatch is
        # deleted, a lambda would keep calling into a dead C++ object.
        palette_signals.changed.connect(self._on_palette_changed)

    def _on_palette_changed(self, *args):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colour = Palette.color(self.color_key)

        if self.kind in (LINE, DASHED_LINE):
            pen = QPen(colour)
            pen.setWidth(2)
            if self.kind == DASHED_LINE:
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setDashPattern([2, 1.5])
            painter.setPen(pen)
            y = self.height() / 2
            painter.drawLine(0, int(y), self.width(), int(y))
            return

        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        painter.setBrush(colour)

        if self.kind == DASHED_SQUARE:
            pen = QPen(Palette.color(f"{self.color_key}_border"))
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setWidth(1)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRect(rect)


class ChartLegend(QWidget):
    """Card title, legend items and an optional note, on one line.

    Replaces the QtCharts legend, which can only sit inside the plot and
    cannot show a dashed bar or a dashed line the way the series draw them.
    """

    def __init__(
        self,
        parent=None,
        title: str = None,
        items: list[tuple[str, str, str]] = (),
        note: str = None,
    ):
        """
        Args:
            title (str, optional): card title shown first. Defaults to None.
            items (list, optional): (text, palette_key, kind) per legend item.
                Defaults to ().
            note (str, optional): small text pushed to the right edge.
                Defaults to None.
        """
        super().__init__(parent)

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(14)

        self.title_label = QLabel(self)
        self.title_label.setObjectName("cardTitle")
        self.widget_layout.addWidget(self.title_label)

        self.items_widget = QWidget(self)
        self.items_layout = QHBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(14)
        self.widget_layout.addWidget(self.items_widget)

        self.widget_layout.addStretch()

        self.note_label = QLabel(self)
        self.note_label.setObjectName("chartNote")
        self.widget_layout.addWidget(self.note_label)

        self.set_title(title)
        self.set_items(items)
        self.set_note(note)

    def set_title(self, title: str = None):
        self.title_label.setText(title or "")

    def set_items(self, items: list[tuple[str, str, str]]):
        """Replace the legend items. An empty list hides the group."""
        while self.items_layout.count():
            child = self.items_layout.takeAt(0).widget()
            if child is not None:
                child.deleteLater()

        for text, color_key, kind in items:
            self.items_layout.addWidget(self._item(text, color_key, kind))

        self.items_widget.setVisible(bool(items))

    def set_note(self, note: str = None):
        self.note_label.setText(note or "")
        self.note_label.setVisible(bool(note))

    def _item(self, text: str, color_key: str, kind: str) -> QWidget:
        item = QWidget(self.items_widget)
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(6)

        swatch = LegendSwatch(item, color_key=color_key, kind=kind)

        label = QLabel(text, item)
        label.setObjectName("chartLegendItem")

        item_layout.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignVCenter)
        item_layout.addWidget(label)
        return item
