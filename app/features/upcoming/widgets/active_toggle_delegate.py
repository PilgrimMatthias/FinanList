from PySide6.QtCore import Qt, QRect, QEvent, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate


class ActiveToggleDelegate(QStyledItemDelegate):
    """Renders a pill toggle for the is_active column. Emits recurring_id on click."""

    toggled = Signal(int)  # emits recurring_id (stable across sort/reload)

    TRACK_W = 36
    TRACK_H = 18
    KNOB = 14
    ON_COLOR = QColor("#1D9E75")
    OFF_COLOR = QColor("#808080")

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        data = index.data(Qt.UserRole)
        if data is None:
            super().paint(painter, option, index)
            return

        is_active, _ = data  # (is_active: bool, recurring_id: int)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        x = option.rect.x() + (option.rect.width() - self.TRACK_W) // 2
        y = option.rect.y() + (option.rect.height() - self.TRACK_H) // 2
        track = QRect(x, y, self.TRACK_W, self.TRACK_H)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.ON_COLOR if is_active else self.OFF_COLOR)
        painter.drawRoundedRect(track, self.TRACK_H // 2, self.TRACK_H // 2)

        knob_x = (x + self.TRACK_W - self.KNOB - 2) if is_active else (x + 2)
        knob_y = y + (self.TRACK_H - self.KNOB) // 2
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QRect(knob_x, knob_y, self.KNOB, self.KNOB))

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            data = index.data(Qt.UserRole)
            if data is not None:
                _, recurring_id = data
                self.toggled.emit(recurring_id)
                return True
        return False