from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QWidget, QHBoxLayout
from app.core.widgets.line_frames import HLine
from app.core.widgets.buttons import PushButton
from app.features.upcoming.models import RecurringTransactionDisplay
from app.core.utils import format_balance, cast_date_to_proper_format
from app.core.enums import OperationType


class UpcomingCard(QFrame):
    """
    Upcoming card widget presents upcoming transactions.
    These are signel operations planned for near future - not list of recurring one.
    """
    review_signal = Signal()

    def __init__(self,upcomings: list[RecurringTransactionDisplay] = None, parent=None):
        super().__init__(parent=parent)
        self.upcomings = upcomings

        self.setObjectName("upcomingCard")


        top_row = QWidget(self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0,0,0,5)

        self.top_title = QLabel(self)
        self.top_title.setText("Coming up")
        self.top_title.setObjectName("upcCardTitle")

        self.view_all_btn = PushButton(
            text="View all ->",
            width=90,
            height=30,
            font_size=8,
            alternate_look=True,
            object_name="viewAllButton",
            on_click=lambda: self.review_signal.emit()
        )

        top_layout.addWidget(self.top_title)
        top_layout.addStretch()
        top_layout.addWidget(self.view_all_btn)

        self.bottom_row = QWidget(self)
        self.bottom_layout = QVBoxLayout(self.bottom_row)
        self.bottom_layout.setSpacing(10)
        self.bottom_layout.setContentsMargins(0,0,0,0)

        self.empty_state_label = QLabel(self)
        self.empty_state_label.setText("No upcomings recorded")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setObjectName("upcCardEmptyState")
        self.empty_state_label.hide()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(top_row)
        main_layout.addWidget(self.bottom_row)
        main_layout.addWidget(self.empty_state_label)
        main_layout.addStretch()

    def set_data(self, upcomings: list[RecurringTransactionDisplay]):
        """Set's data"""
        self._clear()

        if not upcomings:
            self.empty_state_label.show()
            self.bottom_row.hide()
        else:            
            self.empty_state_label.hide()
            self.bottom_row.show()
            
            for idx, upcoming in enumerate(upcomings):
                row = self._create_upcoming_row(upcoming=upcoming, hide_line=len(upcomings) - 1 == idx)

                self.bottom_layout.addWidget(row)

    def _create_upcoming_row(self, upcoming:RecurringTransactionDisplay, hide_line:bool = False) -> QWidget:
        """
        Create upcoming row for display in table

        Args:
            upcoming (RecurringTransactionDisplay): upcomming transaction

        Returns:
            QWidget: Upcoming row
        """
        row = QWidget(self)
        row_layout = QVBoxLayout(row)
        row_layout.setSpacing(5)
        row_layout.setContentsMargins(0,0,0,0)

        upcoming_widget = QWidget(self)
        upcoming_layout = QHBoxLayout(upcoming_widget)
        upcoming_layout.setSpacing(5)
        upcoming_layout.setContentsMargins(0,0,0,0)

        name_label = QLabel(self)
        name_label.setText(upcoming.recurring.title)
        name_label.setMinimumWidth(120)
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setObjectName("upcCardRowTitle")

        operation_date_label = QLabel(self)
        operation_date_label.setText(f"{cast_date_to_proper_format(upcoming.recurring.next_due_date, '%d.%m')}")
        operation_date_label.setMinimumWidth(80)
        operation_date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        operation_date_label.setObjectName("upcCardRowDate")

        amount_label = QLabel(self)
        sign = "+" if upcoming.recurring.operation_type == OperationType.INCOME else "-"
        amount_label.setText(f"{sign}{format_balance(upcoming.recurring.amount)}")
        amount_label.setProperty("positive", "true" if upcoming.recurring.operation_type == OperationType.INCOME else "false")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        amount_label.setObjectName("upcCardRowAmount")
        amount_label.setMinimumWidth(90)
        amount_label.style().unpolish(amount_label)
        amount_label.style().polish(amount_label)

        upcoming_layout.addWidget(name_label,stretch=1)
        upcoming_layout.addWidget(operation_date_label)
        upcoming_layout.addWidget(amount_label)

        h_line = HLine()
        if hide_line: h_line.hide()

        row_layout.addWidget(upcoming_widget)
        row_layout.addWidget(h_line)

        return row

    def _clear(self):
        """Clears layout from upcoming rows"""
        while self.bottom_layout.count():
            item = self.bottom_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()