from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QWidget, QHBoxLayout
from app.core.widgets.line_frames import HLine
from app.core.widgets.buttons import PushButton
from app.features.history.models import TransactionDisplay
from app.core.utils import format_balance, cast_date_to_proper_format
from app.core.enums import OperationType



class RecentOperationCard(QFrame):
    """
    Recent operation card presents recent transactions.
    """
    review_signal = Signal()

    def __init__(self,transactions: list[TransactionDisplay] = None, parent=None ):
        super().__init__(parent=parent)
        self.transactions = transactions

        self.setObjectName("recentOperationsCard")

        top_row = QWidget(self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0,0,0,5)

        self.top_title = QLabel(self)
        self.top_title.setText("Recent operations")
        self.top_title.setObjectName("recOperTitle")

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
        self.empty_state_label.setText("No operations recorded")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setObjectName("recOperEmptyState")
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

    def set_data(self, transactions: list[TransactionDisplay]):
        """Set's data in ui"""
        self._clear()

        if not transactions:
            self.empty_state_label.show()
            self.bottom_row.hide()
        else:            
            self.empty_state_label.hide()
            self.bottom_row.show()

            for idx, transaction in enumerate(transactions):
                row = self._create_transaction_row(transaction=transaction, hide_line=len(transactions) - 1 == idx)

                self.bottom_layout.addWidget(row)

    def _create_transaction_row(self, transaction:TransactionDisplay, hide_line:bool = False) -> QWidget:
        """
        Creates transaction row

        Args:
            transaction (TransactionDisplay): transaction to display

        Returns:
            QWidget: Row widget
        """
        row = QWidget(self)
        row_layout = QVBoxLayout(row)
        row_layout.setSpacing(5)
        row_layout.setContentsMargins(0,0,0,0)

        transaction_widget = QWidget(self)
        transaction_layout = QHBoxLayout(transaction_widget)
        transaction_layout.setSpacing(5)
        transaction_layout.setContentsMargins(0,0,0,0)

        name_label = QLabel(self)
        name_label.setText(transaction.transaction.title)
        name_label.setMinimumWidth(100)
        name_label.setObjectName("recOperRowTitle")

        operation_date_label = QLabel(self)
        operation_date_label.setText(f"{cast_date_to_proper_format(transaction.transaction.date, '%d.%m')}")
        operation_date_label.setMinimumWidth(80)
        operation_date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        operation_date_label.setObjectName("recOperRowDate")

        merchant_label = QLabel(self)
        merchant_label.setText(transaction.transaction.merchant or "—")
        merchant_label.setMinimumWidth(80)
        merchant_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        merchant_label.setObjectName("recOperRowMerchant")

        sign = "+" if transaction.transaction.operation_type == OperationType.INCOME else "-"
        amount_label = QLabel(self)
        amount_label.setText(f"{sign}{format_balance(transaction.transaction.amount)}")
        amount_label.setProperty("positive", "true" if transaction.transaction.operation_type == OperationType.INCOME else "false")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        amount_label.setObjectName("recOperRowAmount")
        amount_label.setMinimumWidth(90)
        amount_label.style().unpolish(amount_label)
        amount_label.style().polish(amount_label)

        transaction_layout.addWidget(name_label,stretch=1)
        transaction_layout.addWidget(operation_date_label)
        transaction_layout.addWidget(merchant_label)
        transaction_layout.addWidget(amount_label)

        h_line = HLine()
        if hide_line: h_line.hide()

        row_layout.addWidget(transaction_widget)
        row_layout.addWidget(h_line)

        return row

    def _clear(self):
        """Clears layout with transaction widgets"""
        while self.bottom_layout.count():
            item = self.bottom_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()