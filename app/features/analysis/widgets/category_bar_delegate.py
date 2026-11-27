from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QApplication,
)

from app.core.theme.palette import Palette

BAR_HEIGHT = 10
BAR_RADIUS = 5
AMOUNT_WIDTH = 80
GAP = 10
TRACK_ALPHA = 46


class CategoryBarDelegate(QStyledItemDelegate):
    """Bar plus amount in the Total column of the Trends category table."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        payload = index.data(Qt.UserRole)
        if payload is None:
            super().paint(painter, option, index)
            return

        fraction, color, amount = payload
        style_option = QStyleOptionViewItem(option)
        self.initStyleOption(style_option, index)

        widget = style_option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(
            QStyle.PrimitiveElement.PE_PanelItemViewItem,
            style_option,
            painter,
            widget,
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect.adjusted(12, 0, -12, 0)
        bar_width = max(0, rect.width() - AMOUNT_WIDTH - GAP)

        track_rect = QRect(
            rect.x(),
            rect.y() + (rect.height() - BAR_HEIGHT) // 2,
            bar_width,
            BAR_HEIGHT,
        )

        track = QColor(Palette.color("text_muted"))
        track.setAlpha(TRACK_ALPHA)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track)
        painter.drawRoundedRect(track_rect, BAR_RADIUS, BAR_RADIUS)

        fill_width = int(bar_width * max(0.0, min(1.0, fraction)))
        if fill_width > 0:
            fill_rect = QRect(track_rect.x(), track_rect.y(), fill_width, BAR_HEIGHT)
            painter.setBrush(QColor(color or Palette.color("category_fallback").name()))
            painter.drawRoundedRect(fill_rect, BAR_RADIUS, BAR_RADIUS)

        font = QFont(option.font)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(Palette.color("text_primary"))
        painter.drawText(
            QRect(
                rect.right() - AMOUNT_WIDTH,
                rect.y(),
                AMOUNT_WIDTH,
                rect.height(),
            ),
            int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
            amount,
        )

        painter.restore()
