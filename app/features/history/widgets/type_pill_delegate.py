from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

from app.core.enums import OperationType


class TypePillDelegate(QStyledItemDelegate):
    """Renders operation type as a colored rounded pill."""

    COLORS = {
        OperationType.INCOME: ("#008000", "#b3ffb3"),
        OperationType.EXPENSE: ("#ff3333", "#ffcccc"),
        OperationType.SAVING: ("#1e65c8", "#bcc5f6"),
        OperationType.INVESTMENT: ("#0f1f70", "#bdd4f5"),
    }

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        super().paint(painter, option, index)
        # Get the operation type from the model — see UserRole tip below
        op_type = index.data(Qt.UserRole)

        text_color, bg_color = self.COLORS.get(op_type, ("#888", "#eee"))
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
        painter.setBrush(QColor(bg_color))
        painter.drawRoundedRect(pill_rect, pill_height // 2, pill_height // 2)

        # Draw text
        painter.setPen(QColor(text_color))
        painter.drawText(pill_rect, Qt.AlignCenter, text)

        painter.restore()
