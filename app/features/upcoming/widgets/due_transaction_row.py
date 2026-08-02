from datetime import datetime
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QScrollArea,
    QSizePolicy,
)
from ..models import RecurringTransactionDisplay
from app.database.models import RecurringTransaction, Transaction
from app.core.enums import OperationType, Currency
from app.core import ExpandToggleButton, PushButton, HLine
from .occurence_row import OccurenceRow


class DueTransactionRow(QFrame):
    selection_changed = Signal()
    ROW_LIMIT = 10
    COLLAPSE_THRESHOLD = 30

    def __init__(self, recurring_display: RecurringTransactionDisplay, parent=None):
        super().__init__(parent)
        self.rec_display = recurring_display
        self._occurrences = recurring_display.occurrences

        # Single source of truth: indices of checked occurrences (checked by default)
        self._checked: set[int] = set(range(len(self._occurrences)))
        self.occurences_rows: list[OccurenceRow] = []
        self._rendered = False

        self._create_row()

    def _create_row(self):
        self.setObjectName("dueTransactionRow")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # Title row
        title_widget = QWidget(self)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setSpacing(5)
        title_layout.setContentsMargins(0, 0, 0, 5)

        self.expand_btn = ExpandToggleButton(on_click=self._is_collapsed)
        self.expand_btn.set_expanded(True)

        self.title_label = QLabel(self)
        self.title_label.setObjectName("dueRowTitle")
        self.title_label.setText(self.rec_display.recurring.title)

        self.interval_label = QLabel(self)
        self.interval_label.setObjectName("dueRowInterval")
        self.interval_label.setText(self.rec_display.recurring.recurrence_interval)

        self.amount_label = QLabel(self)
        self.amount_label.setText(
            self._set_amount(
                recurring=self.rec_display.recurring,
                currency=self.rec_display.currency,
            )
        )
        self.amount_label.setObjectName("dueRowAmount")
        self.amount_label.setProperty("operation", self.rec_display.recurring.operation_type.name.lower())
        
        title_layout.addWidget(self.expand_btn)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.interval_label)
        title_layout.addStretch()
        title_layout.addWidget(self.amount_label)

        # Buttons row 
        buttons_widget = QWidget(self)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(5)
        buttons_layout.setContentsMargins(10, 5, 5, 5)

        self.count_label = QLabel(self)
        self.count_label.setObjectName("dueRowCount")
        self._update_count_label()

        self.confirm_all_btn = PushButton(
            text="Select all",
            width=85,
            height=25,
            font_size=8,
            alternate_look=True,
            on_click=self._confirm_all,
        )
        self.skip_all_btn = PushButton(
            text="Clear",
            width=80,
            height=25,
            font_size=8,
            alternate_look=True,
            object_name="dueSkipButton",
            on_click=self._skip_all,
        )
        self.review_btn = PushButton(
            text="Review",
            width=80,
            height=25,
            font_size=8,
            alternate_look=False,
            on_click=self._on_review_click,
        )
        self.review_btn.setVisible(False)

        buttons_layout.addWidget(self.count_label)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.confirm_all_btn)
        buttons_layout.addWidget(self.skip_all_btn)
        buttons_layout.addWidget(self.review_btn)

        # --- Summary (shown instead of rows for capped groups) ---
        self._summary_widget = QLabel("")
        self._summary_widget.setObjectName("dueRowSummary")
        self._summary_widget.setContentsMargins(10, 10, 0, 0)
        self._summary_widget.hide()

        # --- Scroll area holding occurrence rows ---
        self.scroll_area = InnerScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.occurences_widget = QWidget(self)
        self.scroll_area.setWidget(self.occurences_widget)
        self.occurences_layout = QVBoxLayout(self.occurences_widget)
        self.occurences_layout.setSpacing(5)
        self.occurences_layout.setContentsMargins(5, 5, 5, 0)

        # Small groups render immediately; large groups collapse behind "Review"
        if len(self._occurrences) < self.COLLAPSE_THRESHOLD:
            self._render_rows()
            self._apply_scroll_height()
            self._summary_widget.setText(self._set_summary_text())
        else:
            self.scroll_area.hide()
            self.expand_btn.set_expanded(False)
            self.review_btn.show()
            self._summary_widget.setText(self._set_summary_text())
            self._summary_widget.show()

        self.hline_1 = HLine()
        self.hline_2 = HLine()

        # --- Main layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(title_widget)
        main_layout.addWidget(self.hline_1)
        main_layout.addWidget(buttons_widget)
        main_layout.addWidget(self.hline_2)
        main_layout.addWidget(self._summary_widget)
        main_layout.addWidget(self.scroll_area)

    # Rendering
    def _render_rows(self):
        """Build occurrence row widgets and sync their checkbox to self._checked."""
        if self._rendered:
            return

        for idx, transaction in enumerate(self._occurrences):
            row = OccurenceRow(transaction=transaction)
            row.set_checked(idx in self._checked)

            row.selection_changed.connect(lambda i=idx: self._on_row_toggled(i))
            self.occurences_rows.append(row)
            self.occurences_layout.addWidget(row)

            if idx < len(self._occurrences) - 1:
                self.occurences_layout.addWidget(HLine())

        self._rendered = True

    def _apply_scroll_height(self):
        self.occurences_widget.adjustSize()
        content_h = self.occurences_widget.sizeHint().height()
        cap_h = self._calc_max_height(self.occurences_layout, self.ROW_LIMIT)
        self.scroll_area.setFixedHeight(min(content_h, cap_h))

    def _calc_max_height(self, layout: QVBoxLayout, row_limit: int) -> int:
        """Height of exactly `row_limit` rows plus separators and margins."""
        if not self.occurences_rows:
            return 0

        row_h = self.occurences_rows[0].sizeHint().height()

        line_h = 1
        if layout.count() > 1:
            second = layout.itemAt(1).widget()
            if second is not None:
                line_h = second.sizeHint().height()

        spacing = layout.spacing()
        margins = layout.contentsMargins()
        element_count = row_limit + (row_limit - 1)

        return int(
            row_limit * row_h
            + (row_limit - 1) * line_h
            + (element_count - 1) * spacing
            + margins.top()
            + margins.bottom()
        )

    # Selection state
    def _on_row_toggled(self, idx: int):
        if self.occurences_rows[idx].is_checked():
            self._checked.add(idx)
        else:
            self._checked.discard(idx)
        self._update_count_label()
        self.selection_changed.emit()

    def _confirm_all(self):
        """Check every occurrence in this group."""
        self._set_all_checked(True)

    def _skip_all(self):
        """Uncheck every occurrence in this group."""
        self._set_all_checked(False)

    def _set_all_checked(self, checked: bool):
        self._checked = set(range(len(self._occurrences))) if checked else set()
        if self._rendered:
            for i, row in enumerate(self.occurences_rows):
                row.set_checked(i in self._checked)
        self._update_count_label()
        self.selection_changed.emit()

    def set_occurences_checked(self, checked: bool):
        """External API (e.g. dialog-level Select all / Skip all)."""
        self._set_all_checked(checked)

    def get_checked_transactions(self) -> list[Transaction]:
        return [self._occurrences[i] for i in sorted(self._checked)]


    def is_all_checked(self) -> bool:
        return len(self._checked) == len(self._occurrences)

    def get_recurring_id(self) -> int:
        return self.rec_display.recurring.id

    # Expand
    def _is_collapsed(self):
        if not self._rendered:
            self._on_review_click()
            return
        
        self.expand_btn.toggle()
        self.scroll_area.setVisible(self.expand_btn.is_expanded())

        show = self.scroll_area.isHidden()
        self.review_btn.setText("Collapse" if not show else "Review")
        self._summary_widget.setVisible(show)


    def _on_review_click(self):
        if not self._rendered:
            self._render_rows()
            self._apply_scroll_height()

        show = self.scroll_area.isHidden()
        self.scroll_area.setVisible(show)
        self._summary_widget.setVisible(not show)
        self.expand_btn.set_expanded(show)
        self.review_btn.setText("Collapse" if show else "Review")

    # helpers
    def _update_count_label(self):
        total = len(self._occurrences)
        selected = len(self._checked)
        self.count_label.setText(f"{total} occurrences · {selected} selected")

    def _set_amount(self, recurring: RecurringTransaction, currency: Currency):
        amount = recurring.amount
        sign = "+" if recurring.operation_type == OperationType.INCOME else "-"
        return f"{sign}{amount:,.2f} {currency.name}".replace(",", " ").replace(".", ",")

    def _set_summary_text(self):
        dates = [t.date for t in self._occurrences]
        min_date = min(dates)
        max_date = max(dates)
        # Handles both datetime and ISO-string dates
        fmt = lambda d: d.strftime("%d.%m.%Y") if hasattr(d, "strftime") else str(d)

        if len(dates) == 1:
            return f"{fmt(min_date)}"
        return f"{fmt(min_date)} -> {fmt(max_date)}"


class InnerScrollArea(QScrollArea):
    """Scroll area that hands wheel events to its parent when at a scroll limit,
    so nesting inside another scroll area doesn't trap the user."""

    def wheelEvent(self, event):
        bar = self.verticalScrollBar()
        at_top = bar.value() == bar.minimum()
        at_bottom = bar.value() == bar.maximum()
        scrolling_up = event.angleDelta().y() > 0

        if (at_top and scrolling_up) or (at_bottom and not scrolling_up):
            event.ignore()
            return

        super().wheelEvent(event)