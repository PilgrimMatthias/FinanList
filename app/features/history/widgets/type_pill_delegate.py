from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from app.core.theme.palette import Palette

from app.core.enums import OperationType


class TypePillDelegate(QStyledItemDelegate):
    """Renders operation type as a colored rounded pill."""


    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        super().paint(painter, option, index)
        # Get the operation type from the model — see UserRole tip below
        op_type = index.data(Qt.UserRole)
        if op_type is None:
            return

        bg_color = Palette.operation(op_type, "pill_bg")
        text_color = Palette.operation(op_type, "pill_text")
        text = op_type

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Set up font and measure
        font = QFont(option.font)
        font.setPointSize(10)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        # Pill dimensions
        padding_h = 10
        padding_v = 3
        pill_width = text_width + padding_h * 2
        pill_height = text_height + padding_v * 2

        # Center pill vertically and align left in cell
        x = option.rect.x() + (option.rect.width() - pill_width) // 2
        y = option.rect.y() + (option.rect.height() - pill_height) // 2
        pill_rect = QRect(x, y, pill_width, pill_height)

        # Draw pill background (fully rounded with high radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(pill_rect, pill_height // 2, pill_height // 2)

        # Draw text
        painter.setPen(text_color)
        painter.drawText(pill_rect, Qt.AlignCenter, text)

        painter.restore()
