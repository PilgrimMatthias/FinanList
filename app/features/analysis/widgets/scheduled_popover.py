from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout

from app.core.utils import format_balance
from .chart_helpers import MONTHS_SHORT

MAX_VISIBLE = 8


class ScheduledPopover(QFrame):
    """What the Yet-to-pay figure is made of."""

    def __init__(self, parent=None, occurrences: list = None):
        """
        Args:
            occurrences (list, optional): unconfirmed Transaction occurrences
                for the current month, any order. Defaults to None.
        """
        super().__init__(parent, Qt.WindowType.Popup)

        self.setObjectName("schedulePopover")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(12, 10, 12, 10)
        widget_layout.setSpacing(6)

        occurrences = sorted(occurrences or [], key=lambda t: t.date)
        total = sum(t.amount for t in occurrences)

        if not occurrences:
            empty = QLabel("Nothing left to pay this month.", self)
            empty.setObjectName("popoverEmpty")
            widget_layout.addWidget(empty)
            return

        for occurrence in occurrences[:MAX_VISIBLE]:
            widget_layout.addLayout(
                self._row(
                    f"{occurrence.title} · {self._short_date(occurrence.date)}",
                    format_balance(occurrence.amount),
                )
            )

        hidden = len(occurrences) - MAX_VISIBLE
        if hidden > 0:
            more = QLabel(f"+ {hidden} more", self)
            more.setObjectName("popoverMore")
            widget_layout.addWidget(more)

        separator = QFrame(self)
        separator.setObjectName("popoverSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        widget_layout.addWidget(separator)

        widget_layout.addLayout(
            self._row("Total", format_balance(total), object_name="popoverTotal")
        )

    def show_under(self, anchor, offset: int = 4):
        """Drop the popover under a widget, nudged back on screen if needed."""
        self.adjustSize()

        position = anchor.mapToGlobal(QPoint(0, anchor.height() + offset))
        screen = anchor.screen().availableGeometry()

        # Right edge first, then bottom - a popover that opens off screen is
        # indistinguishable from one that did not open.
        if position.x() + self.width() > screen.right():
            position.setX(screen.right() - self.width())
        if position.y() + self.height() > screen.bottom():
            position.setY(anchor.mapToGlobal(QPoint(0, 0)).y() - self.height() - offset)

        self.move(position)
        self.show()

    def _row(self, text: str, amount: str, object_name: str = "popoverRow"):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        title = QLabel(text, self)
        title.setObjectName(object_name)

        value = QLabel(amount, self)
        value.setObjectName(object_name)
        value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(value)
        return row

    @staticmethod
    def _short_date(value) -> str:
        return f"{value.day} {MONTHS_SHORT[value.month - 1]}"
