# core/widgets/checkbox_delegate.py
from PySide6.QtCore import Qt, QRect, QEvent, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QStyledItemDelegate


class CheckboxDelegate(QStyledItemDelegate):
    """Custom-styled checkbox delegate with theme-aware colors."""

    SIZE = 18
    BORDER_RADIUS = 4
    BORDER_WIDTH = 1.5

    # Colors — adjust to match your theme
    BORDER_COLOR = QColor("#808080")
    BORDER_COLOR_HOVER = QColor("#2a82da")
    FILL_COLOR_CHECKED = QColor("#2a82da")
    FILL_COLOR_UNCHECKED = QColor("#ffffff")
    CHECKMARK_COLOR = QColor("#ffffff")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hover_index = None

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        check_state = index.data(Qt.CheckStateRole)
        if check_state is None:
            return

        is_checked = check_state == Qt.Checked
        is_hovered = self._hover_index == (index.row(), index.column())

        # Center checkbox in cell
        x = option.rect.x() + (option.rect.width() - self.SIZE) // 2
        y = option.rect.y() + (option.rect.height() - self.SIZE) // 2
        rect = QRect(x, y, self.SIZE, self.SIZE)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Border / background
        if is_checked:
            painter.setBrush(QBrush(self.FILL_COLOR_CHECKED))
            painter.setPen(QPen(self.FILL_COLOR_CHECKED, self.BORDER_WIDTH))
        else:
            border = self.BORDER_COLOR_HOVER if is_hovered else self.BORDER_COLOR
            painter.setBrush(QBrush(self.FILL_COLOR_UNCHECKED))
            painter.setPen(QPen(border, self.BORDER_WIDTH))

        painter.drawRoundedRect(rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # Checkmark
        if is_checked:
            pen = QPen(self.CHECKMARK_COLOR, 2.0)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            # Draw checkmark shape — two lines forming a ✓
            cx, cy = rect.center().x(), rect.center().y()
            painter.drawLine(
                QPoint(cx - 4, cy),
                QPoint(cx - 1, cy + 3),
            )
            painter.drawLine(
                QPoint(cx - 1, cy + 3),
                QPoint(cx + 5, cy - 3),
            )

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if not (index.flags() & Qt.ItemIsUserCheckable):
            return False

        if event.type() == QEvent.MouseMove:
            new_hover = (index.row(), index.column())
            if self._hover_index != new_hover:
                self._hover_index = new_hover
            return False

        if event.type() == QEvent.MouseButtonRelease:
            current = index.data(Qt.CheckStateRole)
            new_state = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            return model.setData(index, new_state, Qt.CheckStateRole)

        return False
