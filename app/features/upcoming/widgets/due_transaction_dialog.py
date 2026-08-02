from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QScrollArea
from app.config import DUE_TRANSACTION_DIALOG_HEIGHT, DUE_TRANSACTION_DIALOG_WIDTH
from ..service import UpcomingService
from .due_transaction_row import DueTransactionRow
from app.core import (
    HLine,
    Frame,
    PushButton
)

class DueTransactionDialog(QDialog):
    """
    Due transactions dialog where user can see what transactions are due and can review them by:
    - skipping them
    - confirminh them and advancing recurring transaction due datw

    """
    def __init__(self, service: UpcomingService, parent = None,):
        super().__init__(parent)

        self.service = service

        self.sub_title_text = "You have {num_due} recurring transactions due."

        self._init_dialog()

    def _init_dialog(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFixedWidth(DUE_TRANSACTION_DIALOG_WIDTH)
        self.setFixedHeight(DUE_TRANSACTION_DIALOG_HEIGHT)

        # Title
        self.title_label = QLabel(self)
        self.title_label.setText("Pending Recurring Transactions")
        self.title_label.setObjectName("dueDialogTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Sub title
        self.sub_title_label = QLabel(self)
        self.sub_title_label.setObjectName("dueDialogSubtitle")
        self.sub_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_sub_title_label()

        # Due transaction rows
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        due_tr_widget = QWidget(self)
        scroll_area.setWidget(due_tr_widget)
        due_tr_layout = QVBoxLayout(due_tr_widget)
        due_tr_layout.setSpacing(10)
        due_tr_layout.setContentsMargins(5, 5, 5, 5)

        self.due_transactions = self.service.get_due_transactions(wallet_id=self.service.app_state.active_wallet_id)

        self.due_tr_rows = []

        for due_transaction in self.due_transactions:
            due_tr_row = DueTransactionRow(
                recurring_display=due_transaction
            )
            due_tr_row.selection_changed.connect(self._set_select_btn_text)

            self.due_tr_rows.append(due_tr_row)
            due_tr_layout.addWidget(due_tr_row)

        due_tr_layout.addStretch()
        # Horizontal line
        self.hline = HLine()
        self.hline_2 = HLine()


        # Buttons widget
        button_frame = Frame(self, add_stylesheet=False)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)


        self.select_all_btn = PushButton(
            text="Deselect all" ,
            width=90,
            height=30,
            font_size=9,
            alternate_look=True, 
            on_click=self._select_all,
        )

        self.skip_all_btn = PushButton(
            text="Skip all",
            width=90,
            height=30,
            bg_color="#ff9999",
            bg_color_clicked="#ff3333",
            font_size=9,
            alternate_look=True, 
            on_click=self._skip_transactions
        )

        self.confirm_btn = PushButton(
            text="Confirm Selected",
            width=170,
            height=30,
            font_size=9,
            on_click=self._confirm_selected
        )


        button_layout.addWidget(self.select_all_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(self.skip_all_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.confirm_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)


        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)

        # Add widgets
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.sub_title_label)
        main_layout.addWidget(self.hline)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.hline_2)
        main_layout.addWidget(button_frame)

        self._set_select_btn_text()

    def _set_sub_title_label(self):
        """Set sub title text"""
        num_due = self.service.get_due_count(wallet_id=self.service.app_state.active_wallet_id)

        self.sub_title_label.setText(self.sub_title_text.format(num_due = num_due))

    def _set_select_btn_text(self):
        """Set select btn text and confirmation text with number transaction checked"""
        all_checked = [row for row in self.due_tr_rows if row.is_all_checked()]

        if len(all_checked) != len(self.due_tr_rows):
            self.select_all_btn.set_btn_text("Select all")
        else:
            self.select_all_btn.set_btn_text("Deselect all")

        checked_transactions = [row.get_checked_transactions() for row in self.due_tr_rows]
        checked_transactions = [i for s in checked_transactions for i in s]

        if len(checked_transactions) > 0:
            self.confirm_btn.set_btn_text(f"Confirm Selected ({len(checked_transactions)})")
        else:
            self.confirm_btn.set_btn_text(f"Confirm Selected")


    def _select_all(self):
        """Select all transactions"""
        all_checked = [row for row in self.due_tr_rows if row.is_all_checked()]

        if len(all_checked) == len(self.due_tr_rows):
            for row in self.due_tr_rows:
                row.set_occurences_checked(False)

            self.select_all_btn.set_btn_text("Select all")
        else:
            for row in self.due_tr_rows:
                row.set_occurences_checked(True)
            self.select_all_btn.set_btn_text("Deselect all")

    def _skip_transactions(self):
        """Skip all transactions"""
        self.close()

    def _confirm_selected(self):
        """Confirm selected transactions"""
        checked_transactions = [row.get_checked_transactions() for row in self.due_tr_rows]
        checked_transactions = [i for s in checked_transactions for i in s]

        if len(checked_transactions) == 0:
            return

        # Confirm transaction
        self.service.confirm_transactions(checked_transactions)

        # Advance recurring if possible
        self.service.advance_recurrings(recurrings=self.due_transactions, confirmed=checked_transactions)

        self.close()





