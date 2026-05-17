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
    QFileDialog,
    QStackedWidget,
    QLabel,
)
from app.core import Frame, PushButton, show_error, show_confirmation, SvgIcon
from app.core.exceptions import ValidationError
from app.core.constants import DEF_TRANSACTION_EXPORT_FILE_NAME
from app.core.app_state import AppState
from app.config import SEARCH_ICON, EMPTY_TRANSACTIONS
from .service import HistoryService
from .widgets.history_table import HistoryTableModel
from .widgets.checkbox_delegate import CheckboxDelegate
from .widgets.pagination_widget import PaginationWidget
from .widgets.category_dot_delegate import CategoryDotDelegate
from .widgets.type_pill_delegate import TypePillDelegate

from datetime import datetime

from ..transaction.service import TransactionService
from ..transaction.view import TransactionView


# Placeholder — just enough to test sidebar switching
class HistoryView(QWidget):
    SORT_KEYS = {
        1: "title",
        2: "merchant",
        3: "date",
        4: "type",
        5: "category",
        6: "amount",
    }

    def __init__(
        self,
        service: HistoryService,
        transaction_service: TransactionService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.transaction_service = transaction_service
        self.app_state = app_state

        self._init_view()

        self.app_state.wallet_changed.connect(self._reload)
        self.app_state.transaction_changed.connect(self._reload)

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

        self.select_all_btn = PushButton(
            text="Select all",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_select_all,
        )
        self.select_all_btn.hide()

        self.export_btn = PushButton(
            text="Export",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_export_clicked,
        )

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
        self.search_box.setPlaceholderText("Search transactions...")
        self.search_box.setMinimumWidth(250)
        self.search_box.setMaximumWidth(400)
        self.search_box.editingFinished.connect(self._on_editing_finished)

        icon = QIcon(str(SEARCH_ICON))
        self.search_box.addAction(icon, QLineEdit.LeadingPosition)

        top_btn_layout.addWidget(self.select_btn)
        top_btn_layout.addWidget(self.select_all_btn)
        top_btn_layout.addWidget(self.export_btn)
        top_btn_layout.addWidget(self.delete_btn)
        top_btn_layout.addStretch()
        top_btn_layout.addWidget(self.search_box)

        # Table
        self.history_table_model = HistoryTableModel(
            service=self.service, app_state=self.app_state
        )
        self.history_table_model.checkbox_clicked.connect(self._on_checkbox_clicked)
        self.history_table = QTableView()
        self.history_table.setModel(self.history_table_model)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history_table.setShowGrid(False)
        self.history_table.verticalHeader().hide()
        self.history_table.verticalHeader().setDefaultSectionSize(45)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setSectionResizeMode(
            # QHeaderView.Stretch
            QHeaderView.Interactive
        )
        self.history_table.horizontalHeader().setSortIndicatorShown(True)
        self.history_table.horizontalHeader().sectionClicked.connect(
            self._on_header_clicked
        )
        self.history_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )  # Prevent inline editing

        # Item delegates
        self._checkbox_delegate = CheckboxDelegate()
        self._type_delegate = TypePillDelegate()
        self._category_delegate = CategoryDotDelegate()
        self.history_table.setItemDelegateForColumn(0, self._checkbox_delegate)
        self.history_table.setItemDelegateForColumn(
            self.history_table_model.TYPE_COL, self._type_delegate
        )
        self.history_table.setItemDelegateForColumn(
            self.history_table_model.CATEGORY_COL, self._category_delegate
        )

        self.history_table.setColumnHidden(0, True)
        self.history_table.setColumnWidth(0, 10)
        self.history_table.doubleClicked.connect(self._on_edit_transaction)

        # State - no transactions found
        self.no_transaction_in_db_widget = QWidget()
        no_tr_in_db_layout = QVBoxLayout(self.no_transaction_in_db_widget)
        no_tr_in_db_layout.setContentsMargins(0, 0, 0, 0)
        no_tr_in_db_layout.setSpacing(10)

        empty_tr_icon = SvgIcon(self, file=str(EMPTY_TRANSACTIONS))
        empty_tr_icon.setFixedSize(80, 80)

        self.ntd_top_label = QLabel(self)
        self.ntd_top_label.setText(
            "No transactions yet.",
        )
        self.ntd_top_label.setObjectName("not_tr_label")
        self.ntd_top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ntd_bottom_label = QLabel(self)
        self.ntd_bottom_label.setText(
            'Click "Add transaction" in the sidebar to record your first one.',
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
        self.stacked_states.addWidget(self.history_table)
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
        self.history_table_model.reload()
        self._total_wallet_count = self.service.get_count(wallet_id=wallet_id)

        # Update column width
        for i in range(1, self.history_table_model.columnCount()):
            self.history_table.setColumnWidth(i, 125)

        self._update_ui()

    def _update_ui(self):
        """Refresh pagination, buttons, empty state — without re-querying model"""
        self.pagination_widget.reload(
            current_page=self.history_table_model.current_page,
            total_pages=self.history_table_model.total_pages(),
            total_count=self.history_table_model.total_count,
        )

        self._update_select_all_btn()
        self._on_checkbox_clicked()
        self._update_empty_state()

    def _update_select_all_btn(self):
        if not self.history_table_model.is_selection_mode:
            return

        if self.history_table_model.all_selected():
            self.select_all_btn.setText("Deselect all")
        else:
            self.select_all_btn.setText("Select all")

    def _update_empty_state(self):

        # Show state based on number of transactions
        if self._total_wallet_count == 0:
            self.stacked_states.setCurrentIndex(1)

            self.ntd_top_label.setText(
                "No transactions yet.",
            )
            self.ntd_bottom_label.setText(
                'Click "Add transaction" in the sidebar to record your first one.',
            )

        elif self.history_table_model.rowCount() == 0 and self._total_wallet_count > 0:
            self.ntd_top_label.setText(
                "No transactions found.",
            )
            self.ntd_bottom_label.setText(
                "",
            )
            self.stacked_states.setCurrentIndex(1)
        else:
            self.stacked_states.setCurrentIndex(0)

    # SELECTION MODES
    def _set_selection_mode(self):
        if self.history_table_model.is_selection_mode:
            self._exit_selection_mode()
        else:
            self._enter_selection_mode()

    def _enter_selection_mode(self):
        """Enter selection mode in ui - changes visibility of checkbox and button names"""
        self.history_table.setColumnHidden(0, False)
        self.history_table_model.set_selection_mode(True)

        self.select_btn.setText("Cancel")
        self.export_btn.setText("Export selected")
        self.export_btn.set_width(120)
        self.select_all_btn.show()
        self.delete_btn.show()

    def _exit_selection_mode(self):
        """Exit selection mode in ui - changes visibility of checkbox and button names"""
        self.history_table.setColumnHidden(0, True)
        self.history_table_model.set_selection_mode(False)

        self.select_btn.setText("Select")
        self.export_btn.setText("Export")
        self.select_all_btn.setText("Select all")
        self.export_btn.set_width(100)
        self.select_all_btn.hide()
        self.delete_btn.hide()

    def _on_select_all(self):
        """On select all button click - toggle selecction in table model and changes btn names"""
        self.history_table_model.toggle_select_all()

        if self.history_table_model.all_selected():
            self.select_all_btn.setText("Deselect all")
        else:
            self.select_all_btn.setText("Select all")

    def _on_header_clicked(self, section: int):
        """On table view header click - triggers sorting mechanism"""
        sort_key = self.SORT_KEYS.get(section)

        if sort_key is None:
            return

        current_key = self.history_table_model.sort_by
        current_order = self.history_table_model.sort_order

        new_order = "DESC"
        if sort_key == current_key:
            new_order = "ASC" if current_order == "DESC" else "DESC"

        self.history_table_model.set_sort(column=sort_key, order=new_order)

        qt_order = Qt.DescendingOrder if new_order == "DESC" else Qt.AscendingOrder
        self.history_table.horizontalHeader().setSortIndicator(section, qt_order)

    def _on_editing_finished(self):
        """On editing finished of Search box - triggers serach service"""
        text = self.search_box.text()

        self.history_table_model.set_search(query=text)

        self._update_ui()

    def _on_navigation_signal(self, page: int):
        self.history_table_model.set_page(page=page)

        self._update_ui()

    def _on_checkbox_clicked(self):
        """On check box click in table - sets delete btn text with proper number of selected rows"""
        selected_count = len(self.history_table_model.get_selected_ids())
        if selected_count > 0:
            self.delete_btn.setText(f"Delete ({selected_count})")
        else:
            self.delete_btn.setText("Delete")

    def _on_delete_clicked(self):
        """On delete click - ask user about deletion - delets selected ids.

        If none is selected informs user abaout that situation.
        """
        transactions_to_delete = self.history_table_model.get_selected_ids()

        if len(transactions_to_delete) == 0:
            message = "No transactions to delete!\nSelect transaction to delete them"
            show_error(self, message=message, title="Delete error")
            return

        message = f"Delete {len(transactions_to_delete)} transactions?\n\n"
        if show_confirmation(
            self, message, title="Delete transactions", confirm_text="Delete"
        ):
            try:
                self.service.delete_transactions(transactions_to_delete)

                self._exit_selection_mode()
            except ValidationError as e:
                show_error(self, str(e))

    def _on_export_clicked(self):
        """On export btyn clicked - asks user about exporting and shows file dialog to choose save path.

        If none transaction are selected than user can export all the transactions.
        """
        transactions_to_export = self.history_table_model.get_selected_ids()

        if len(transactions_to_export) == 0:
            message = "Do you want to export all transactions?"
            transactions_to_export = self.service.get_all_transactions_ids(
                wallet_id=self.app_state.active_wallet_id
            )
        else:
            message = (
                f"Do you want to export {len(transactions_to_export)} transactions?"
            )

        if show_confirmation(
            self, message, title="Export transactions", confirm_text="Export"
        ):
            save_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                self.tr("Save File"),
                DEF_TRANSACTION_EXPORT_FILE_NAME.format(
                    date=datetime.today().strftime("%d-%m-%Y")
                ),
                self.tr("Excel (*.xlsx);;Comma-separated values (*.csv)"),
            )

            if save_path:
                try:
                    self.service.export_selected(
                        transactions_to_export, save_path=save_path
                    )

                    self._exit_selection_mode()
                except ValidationError as e:
                    show_error(self, str(e))

    def _on_edit_transaction(self, row):
        """On table cell clicked - triggers TransactionView in edit mode to edit the transaction"""
        transaction = self.history_table_model.get_row_transaction(row=row.row())

        dialog = TransactionView(
            parent=self, service=self.transaction_service, transaction=transaction
        )

        dialog.show()
