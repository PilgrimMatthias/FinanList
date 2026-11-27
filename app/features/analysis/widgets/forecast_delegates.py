from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QApplication,
)

from app.core.theme.palette import Palette

CELL_PADDING = 8  # matches the analysis table QSS item padding
BADGE_PADDING_H = 5
BADGE_PADDING_V = 1
BADGE_RADIUS = 4
BADGE_GAP = 6
BADGE_BG_ALPHA = 38
NOTE_POINT_DROP = 2
LINE_GAP = 1

OVER_PLAN_MARKER = "▲"
TO_DATE_TEXT = "to date"
BELOW_FLOOR_TEXT = "below floor"


def draw_background(painter: QPainter, option: QStyleOptionViewItem, delegate, index):
    """Paint the row background and selection, but not the text."""
    style_option = QStyleOptionViewItem(option)
    delegate.initStyleOption(style_option, index)
    style_option.text = ""

    widget = style_option.widget
    style = widget.style() if widget is not None else QApplication.style()
    style.drawPrimitive(
        QStyle.PrimitiveElement.PE_PanelItemViewItem,
        style_option,
        painter,
        widget,
    )


def text_colour(index, fallback: str = "text_primary") -> QColor:
    """Respect the model's ForegroundRole, so the model keeps deciding."""
    colour = index.data(Qt.ForegroundRole)
    return colour if colour is not None else Palette.color(fallback)


class StackedNoteDelegate(QStyledItemDelegate):
    """A right-aligned value with an optional small note under it."""

    def note(self, index) -> tuple[str, QColor] | None:
        """Return (text, colour), or None for a plain cell."""
        raise NotImplementedError

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        note = self.note(index)
        if note is None:
            super().paint(painter, option, index)
            return

        draw_background(painter, option, self, index)

        note_text, note_colour = note
        value = index.data(Qt.DisplayRole) or ""

        painter.save()

        rect = option.rect.adjusted(CELL_PADDING, 0, -CELL_PADDING, 0)

        # Honour the model's FontRole (italic Est. other, bold Closing) -
        # the option handed to paint() has not been through initStyleOption.
        value_font = QFont(option.font)
        model_font = index.data(Qt.FontRole)
        if model_font is not None:
            value_font.setItalic(model_font.italic())
            value_font.setWeight(model_font.weight())
        note_font = self._note_font(option)

        painter.setFont(value_font)
        value_height = painter.fontMetrics().height()
        painter.setFont(note_font)
        note_height = painter.fontMetrics().height()

        total = value_height + LINE_GAP + note_height
        top = rect.y() + (rect.height() - total) // 2
        align = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        painter.setFont(value_font)
        painter.setPen(text_colour(index))
        painter.drawText(QRect(rect.x(), top, rect.width(), value_height), align, value)

        painter.setFont(note_font)
        painter.setPen(note_colour)
        painter.drawText(
            QRect(rect.x(), top + value_height + LINE_GAP, rect.width(), note_height),
            align,
            note_text,
        )

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        """Two lines need the height of two lines.

        A fixed defaultSectionSize on the view overrides this, but the
        hint has to be right for the day the view stops fixing it.
        """
        hint = super().sizeHint(option, index)
        if self.note(index) is None:
            return hint

        extra = QApplication.fontMetrics().height()
        return QSize(hint.width(), hint.height() + extra + LINE_GAP)

    @staticmethod
    def _note_font(option: QStyleOptionViewItem) -> QFont:
        font = QFont(option.font)
        font.setPointSize(max(6, font.pointSize() - NOTE_POINT_DROP))
        font.setWeight(QFont.Weight.DemiBold)
        font.setItalic(False)
        return font


class OverPlanDelegate(StackedNoteDelegate):
    """Marks the Est. other cell when scheduled items exceed the plan."""

    def note(self, index):
        payload = index.data(Qt.UserRole)
        if not payload:
            return None

        over_plan_by, _is_current_month = payload
        if not over_plan_by:
            return None

        return (
            f"{OVER_PLAN_MARKER} {self._amount(over_plan_by)}",
            Palette.color("warning"),
        )

    @staticmethod
    def _amount(value: float) -> str:
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")


class BelowFloorDelegate(StackedNoteDelegate):
    """Labels the Closing cell of a month that lands under the floor."""

    def note(self, index):
        payload = index.data(Qt.UserRole)
        if not payload:
            return None

        below_floor, _floor_gap = payload
        if not below_floor:
            return None

        return BELOW_FLOOR_TEXT, Palette.color("danger")


class ToDateBadgeDelegate(QStyledItemDelegate):
    """Puts a "to date" pill beside the current month's label."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if not index.data(Qt.UserRole):
            super().paint(painter, option, index)
            return

        draw_background(painter, option, self, index)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect.adjusted(CELL_PADDING, 0, -CELL_PADDING, 0)
        text = index.data(Qt.DisplayRole) or ""

        painter.setFont(option.font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)

        painter.setPen(text_colour(index))
        painter.drawText(
            rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            text,
        )

        badge_font = self._badge_font(option)
        painter.setFont(badge_font)
        badge_metrics = painter.fontMetrics()

        badge_width = (
            badge_metrics.horizontalAdvance(TO_DATE_TEXT) + BADGE_PADDING_H * 2
        )
        badge_height = badge_metrics.height() + BADGE_PADDING_V * 2
        badge_rect = QRect(
            rect.x() + text_width + BADGE_GAP,
            rect.y() + (rect.height() - badge_height) // 2,
            badge_width,
            badge_height,
        )

        accent = Palette.color("accent")
        # Copy before setAlpha - Palette.color() returns the cached QColor
        # itself, and mutating it would fade every accent in the app.
        background = QColor(accent)
        background.setAlpha(BADGE_BG_ALPHA)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(badge_rect, BADGE_RADIUS, BADGE_RADIUS)

        painter.setPen(accent)
        painter.drawText(badge_rect, int(Qt.AlignmentFlag.AlignCenter), TO_DATE_TEXT)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        """Reserve the badge, or ResizeToContents clips it.

        The column is sized from the hint, and the base hint only knows
        about the month label.
        """
        hint = super().sizeHint(option, index)
        if not index.data(Qt.UserRole):
            return hint

        badge_metrics = QApplication.fontMetrics()
        badge_width = (
            badge_metrics.horizontalAdvance(TO_DATE_TEXT)
            + BADGE_PADDING_H * 2
            + BADGE_GAP
        )
        return QSize(hint.width() + badge_width, hint.height())

    @staticmethod
    def _badge_font(option: QStyleOptionViewItem) -> QFont:
        font = QFont(option.font)
        font.setPointSize(max(6, font.pointSize() - NOTE_POINT_DROP))
        font.setWeight(QFont.Weight.DemiBold)
        return font
