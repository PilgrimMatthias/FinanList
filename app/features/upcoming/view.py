from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLineEdit,
    QTableView,
    QAbstractItemView,
    QHeaderView,
    QStackedWidget,
    QLabel,
)
from app.core import Frame, PushButton, show_error, show_confirmation, SvgIcon
from app.core.exceptions import ValidationError
from app.core.app_state import AppState
from app.config import SEARCH_ICON, EMPTY_TRANSACTIONS
from .service import UpcomingService
from .widgets.upcoming_table import UpcomingTableModel
from app.core import CheckboxDelegate, CategoryDotDelegate
from .widgets.pagination_widget import PaginationWidget
from .widgets.active_toggle_delegate import ActiveToggleDelegate
from .widgets.due_transaction_dialog import DueTransactionDialog

from ..transaction.service import TransactionService
from ..transaction.view import TransactionView


class UpcomingView(QWidget):
    SORT_KEYS = {
        1: "title",
        2: "interval",
        3: "next_due_date",
        4: "category",
        5: "amount",
        6: "is_active",
    }

    def __init__(
        self,
        service: UpcomingService,
        transaction_service: TransactionService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.transaction_service = transaction_service
        self.app_state = app_state

        self._total_wallet_count = 0

        self._init_view()

        self.app_state.wallet_changed.connect(self._reload)
        self.app_state.recurring_transaction_changed.connect(self._reload)

    def _init_view(self):
        "Initialize view"
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        # Top Buttons frame
        top_btn_frame = Frame(self, add_stylesheet=False)
        top_btn_layout = QHBoxLayout(top_btn_frame)
        top_btn_layout.setSpacing(5)
        top_btn_layout.setContentsMargins(0, 0, 0, 10)

        self.select_btn = PushButton(
            text="Select",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._set_selection_mode,
        )
        self.show_due_dialog = PushButton(
            text="Show due transactions",
            alternate_look=False,
            width=150,
            height=30,
            font_size=9,
            on_click=self._show_due_dialog,
        )
        self.select_all_btn = PushButton(
            text="Select all",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_select_all,
        )
        self.select_all_btn.hide()

        self.delete_btn = PushButton(
            text="Delete",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_delete_clicked,
        )
        self.delete_btn.hide()

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search recurring...")
        self.search_box.setMinimumWidth(250)
        self.search_box.setMaximumWidth(400)
        self.search_box.editingFinished.connect(self._on_editing_finished)

        icon = QIcon(str(SEARCH_ICON))
        self.search_box.addAction(icon, QLineEdit.LeadingPosition)

        top_btn_layout.addWidget(self.show_due_dialog)
        top_btn_layout.addWidget(self.select_btn)
        top_btn_layout.addWidget(self.select_all_btn)

        top_btn_layout.addWidget(self.delete_btn)
        top_btn_layout.addStretch()
        top_btn_layout.addWidget(self.search_box)

        # Table
        self.upcoming_table_model = UpcomingTableModel(
            service=self.service, app_state=self.app_state
        )
        self.upcoming_table_model.checkbox_clicked.connect(self._on_checkbox_clicked)
        self.upcoming_table = QTableView()
        self.upcoming_table.setModel(self.upcoming_table_model)
        self.upcoming_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.upcoming_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.upcoming_table.setShowGrid(False)
        self.upcoming_table.verticalHeader().hide()
        self.upcoming_table.verticalHeader().setDefaultSectionSize(45)
        self.upcoming_table.horizontalHeader().setStretchLastSection(True)
        self.upcoming_table.horizontalHeader().setSectionResizeMode(
            # QHeaderView.Stretch
            QHeaderView.Interactive
        )
        self.upcoming_table.horizontalHeader().setSortIndicatorShown(True)
        self.upcoming_table.horizontalHeader().sectionClicked.connect(
            self._on_header_clicked
        )
        self.upcoming_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )  # Prevent inline editing

        # Item delegates
        self._checkbox_delegate = CheckboxDelegate()
        self._is_active_delegate = ActiveToggleDelegate()
        self._is_active_delegate.toggled.connect(self._on_toggle_active)
        self._category_delegate = CategoryDotDelegate()
        self.upcoming_table.setItemDelegateForColumn(0, self._checkbox_delegate)
        self.upcoming_table.setItemDelegateForColumn(
            self.upcoming_table_model.ACTIVE_COL, self._is_active_delegate
        )
        self.upcoming_table.setItemDelegateForColumn(
            self.upcoming_table_model.CATEGORY_COL, self._category_delegate
        )

        self.upcoming_table.setColumnHidden(0, True)
        self.upcoming_table.setColumnWidth(0, 10)
        self.upcoming_table.doubleClicked.connect(self._on_edit_recurring)

        # State - no transactions found
        self.no_transaction_in_db_widget = QWidget()
        no_tr_in_db_layout = QVBoxLayout(self.no_transaction_in_db_widget)
        no_tr_in_db_layout.setContentsMargins(0, 0, 0, 0)
        no_tr_in_db_layout.setSpacing(10)

        empty_tr_icon = SvgIcon(self, file=str(EMPTY_TRANSACTIONS))
        empty_tr_icon.setFixedSize(80, 80)

        self.ntd_top_label = QLabel(self)
        self.ntd_top_label.setText(
            "No recurring transactions yet.",
        )
        self.ntd_top_label.setObjectName("not_tr_label")
        self.ntd_top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ntd_bottom_label = QLabel(self)
        self.ntd_bottom_label.setText(
            'Create a transaction with a repeat interval to see it here.',
        )
        self.ntd_bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        no_tr_in_db_layout.addStretch()
        no_tr_in_db_layout.addWidget(
            empty_tr_icon, alignment=Qt.AlignmentFlag.AlignCenter
        )
        no_tr_in_db_layout.addWidget(self.ntd_top_label)
        no_tr_in_db_layout.addWidget(self.ntd_bottom_label)
        no_tr_in_db_layout.addStretch()

        self.stacked_states = QStackedWidget()
        self.stacked_states.addWidget(self.upcoming_table)
        self.stacked_states.addWidget(self.no_transaction_in_db_widget)

        # Pagination widget
        self.pagination_widget = PaginationWidget(
            current_page=0, total_pages=0, total_count=0, parent=self
        )
        self.pagination_widget.page_changed.connect(self._on_navigation_signal)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(top_btn_frame)
        main_layout.addWidget(self.stacked_states)
        main_layout.addWidget(self.pagination_widget)
        # main_layout.addStretch()

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    def _reload(self, wallet_id: int):
        """Full reload — model + UI"""
        if wallet_id is None:
            return

        self._exit_selection_mode()
        self.upcoming_table_model.reload()
        self._total_wallet_count = self.service.get_count(wallet_id=wallet_id)

        # Update column width
        for i in range(1, self.upcoming_table_model.columnCount()):
            self.upcoming_table.setColumnWidth(i, 125)

        self._due_count = self.service.get_due_count(wallet_id)

        self._update_ui()

    def _update_ui(self):
        """Refresh pagination, buttons, empty state — without re-querying model"""
        self.pagination_widget.reload(
            current_page=self.upcoming_table_model.current_page,
            total_pages=self.upcoming_table_model.total_pages(),
            total_count=self.upcoming_table_model.total_count,
        )

        if self.upcoming_table_model.total_count > self.upcoming_table_model._page_size:
            self.pagination_widget.show()
        else:
            self.pagination_widget.hide()

        self._update_select_all_btn()
        self._on_checkbox_clicked()
        self._update_empty_state()
        self._show_hide_due_dialog_btn()

    def _show_hide_due_dialog_btn(self):
        """Show/hide due dialog btn"""
        if self._due_count== 0:
            self.show_due_dialog.hide()
        else:
            self.show_due_dialog.show()

    def _update_select_all_btn(self):
        if not self.upcoming_table_model.is_selection_mode:
            return

        if self.upcoming_table_model.all_selected():
            self.select_all_btn.setText("Deselect all")
        else:
            self.select_all_btn.setText("Select all")

    def _update_empty_state(self):

        # Show state based on number of transactions
        if self._total_wallet_count == 0:
            self.stacked_states.setCurrentIndex(1)

            self.ntd_top_label.setText(
                "No recurring transactions yet.",
            )
            self.ntd_bottom_label.setText(
                'Create a transaction with a repeat interval to see it here.',
            )

        elif self.upcoming_table_model.rowCount() == 0 and self._total_wallet_count > 0:
            self.ntd_top_label.setText(
                "No recurring transactions found.",
            )
            self.ntd_bottom_label.setText(
                "",
            )
            self.stacked_states.setCurrentIndex(1)
        else:
            self.stacked_states.setCurrentIndex(0)

    # SELECTION MODES
    def _set_selection_mode(self):
        if self.upcoming_table_model.is_selection_mode:
            self._exit_selection_mode()
        else:
            self._enter_selection_mode()

    def _enter_selection_mode(self):
        """Enter selection mode in ui - changes visibility of checkbox and button names"""
        self.upcoming_table.setColumnHidden(0, False)
        self.upcoming_table_model.set_selection_mode(True)

        self.select_btn.setText("Cancel")
        # self.export_btn.setText("Export selected")
        # self.export_btn.set_width(120)
        self.select_all_btn.show()
        self.delete_btn.show()

    def _exit_selection_mode(self):
        """Exit selection mode in ui - changes visibility of checkbox and button names"""
        self.upcoming_table.setColumnHidden(0, True)
        self.upcoming_table_model.set_selection_mode(False)

        self.select_btn.setText("Select")
        # self.export_btn.setText("Export")
        # self.export_btn.set_width(100)
        self.select_all_btn.setText("Select all")
        self.select_all_btn.hide()
        self.delete_btn.hide()

    def _on_select_all(self):
        """On select all button click - toggle selecction in table model and changes btn names"""
        self.upcoming_table_model.toggle_select_all()

        if self.upcoming_table_model.all_selected():
            self.select_all_btn.setText("Deselect all")
        else:
            self.select_all_btn.setText("Select all")

    def _on_header_clicked(self, section: int):
        """On table view header click - triggers sorting mechanism"""
        sort_key = self.SORT_KEYS.get(section)

        if sort_key is None:
            return

        current_key = self.upcoming_table_model.sort_by
        current_order = self.upcoming_table_model.sort_order

        new_order = "DESC"
        if sort_key == current_key:
            new_order = "ASC" if current_order == "DESC" else "DESC"

        self.upcoming_table_model.set_sort(column=sort_key, order=new_order)

        qt_order = Qt.DescendingOrder if new_order == "DESC" else Qt.AscendingOrder
        self.upcoming_table.horizontalHeader().setSortIndicator(section, qt_order)

    def _on_editing_finished(self):
        """On editing finished of Search box - triggers serach service"""
        text = self.search_box.text()

        self.upcoming_table_model.set_search(query=text)

        self._update_ui()

    def _on_navigation_signal(self, page: int):
        self.upcoming_table_model.set_page(page=page)

        self._update_ui()

    def _on_checkbox_clicked(self):
        """On check box click in table - sets delete btn text with proper number of selected rows"""
        selected_count = len(self.upcoming_table_model.get_selected_ids())
        if selected_count > 0:
            self.delete_btn.setText(f"Delete ({selected_count})")
        else:
            self.delete_btn.setText("Delete")

    def _on_delete_clicked(self):
        """On delete click - ask user about deletion - delets selected ids.

        If none is selected informs user abaout that situation.
        """
        upcomings_to_delete = self.upcoming_table_model.get_selected_ids()

        if len(upcomings_to_delete) == 0:
            message = "No upcomings to delete!\nSelect upcomings to delete them"
            show_error(self, message=message, title="Delete error")
            return

        message = f"Delete {len(upcomings_to_delete)} upcomings transactions?\n\n"
        if show_confirmation(
            self, message, title="Delete transactions", confirm_text="Delete"
        ):
            try:
                self.service.delete_transactions(upcomings_to_delete)

                self._exit_selection_mode()
            except ValidationError as e:
                show_error(self, str(e))

    def _on_toggle_active(self, recurring_id: int):
        """activate or disactive recurrings"""
        try:
            self.service.toggle_active(recurring_id)
            # service emits recurring_transaction_changed → triggers _reload
        except ValidationError as e:
            show_error(self, str(e))

    def _on_edit_recurring(self, row):
        """On table cell clicked - triggers TransactionView in edit mode to edit the transaction"""
        transaction = self.upcoming_table_model.get_row_recurring(row=row.row())

        dialog = TransactionView(
            parent=self, service=self.transaction_service, transaction=transaction
        )

        dialog.show()

    def _show_due_dialog(self):
        """Shows due dialog to confirm transactions"""
    
        if self._due_count > 0:
            dialog = DueTransactionDialog(
                service=self.service,
                parent=self,
            )
            dialog.exec()  