import math
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor, QFont
from ..service import HistoryService
from app.core.app_state import AppState
from ..models import TransactionDisplay
from PySide6.QtCore import Qt

from app.core.enums import OperationType
from app.core.utils import cast_date_to_proper_format


class HistoryTableModel(QAbstractTableModel):
    checkbox_clicked = Signal()

    COLUMNS = ["", "Name", "Merchant", "Date", "Type", "Category", "Amount"]
    CHECKBOX_COL = 0
    TYPE_COL = 4
    CATEGORY_COL = 5

    INCOME_COLOR = QColor("#008000")
    EXPENSE_COLOR = QColor("#ff3333")
    SAVINGS_COLOR = QColor("#1e65c8")
    INVESTMENT_COLOR = QColor("#0f1f70")

    BG_INCOME_COLOR = QColor("#b3ffb3")
    BG_EXPENSE_COLOR = QColor("#ffcccc")
    BG_SAVINGS_COLOR = QColor("#bcc5f6")
    BG_INVESTMENT_COLOR = QColor("#bdd4f5")

    def __init__(self, service: HistoryService, app_state: AppState, parent=None):
        super().__init__(parent)
        self._service = service
        self._app_state = app_state
        self._rows: list[TransactionDisplay] = []
        self._total_count = 0
        self._page = 1
        self._page_size = 100
        self._sort_by = "date"
        self._sort_order = "DESC"
        self._search = ""
        self._is_selection_mode = False
        self._selected_ids: set[int] = set()

    # QAbstractModel method
    def rowCount(self, parent=QModelIndex()) -> int:
        """How many rows? View calls this constantly."""
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        """How many columns?"""
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """What goes in cell at (index.row(), index.column())?"""
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        col = index.column()

        # Checkbox column — handle CheckStateRole
        if col == self.CHECKBOX_COL:
            if role == Qt.CheckStateRole and self._is_selection_mode:
                return (
                    Qt.Checked
                    if row.transaction.id in self._selected_ids
                    else Qt.Unchecked
                )
            return None  # No display text in checkbox column

        # Type col setting
        if col == self.TYPE_COL:
            if role == Qt.UserRole:
                return row.transaction.operation_type  # Pass the enum directly
            if role == Qt.DisplayRole:
                return ""  # Leave empty — delegate handles painting
            return None

        # Category col setting
        if col == self.CATEGORY_COL:
            if role == Qt.UserRole:
                return (
                    row.sub_category_color,
                    f"{row.main_category_name} / {row.sub_category_name}",
                )
            if role == Qt.DisplayRole:
                return ""
            return None

        # Remaining display roles
        if role == Qt.DisplayRole:
            # The text shown in the cell
            if col == 1:
                return row.transaction.title
            if col == 2:
                return row.transaction.merchant or "—"
            if col == 3:
                return cast_date_to_proper_format(row.transaction.date)
            if col == 6:
                amount = row.transaction.amount
                op_type = row.transaction.operation_type
                sign = "+" if op_type == OperationType.INCOME else "−"
                return f"{sign}{amount:,.2f}"

        if role == Qt.TextAlignmentRole:
            if col in [
                1,
                2,
            ]:
                return Qt.AlignVCenter | Qt.AlignLeft
            else:
                return Qt.AlignCenter

        if role == Qt.FontRole:
            if col == 1 and row.is_recurring:  # Recurring transactions — italic
                font = QFont()
                font.setItalic(True)
                return font

        if role == Qt.ForegroundRole:
            if col == 6:
                return self._color_for_type(
                    row.transaction.operation_type, role=Qt.ForegroundRole
                )

        return None  # Always return None for unhandled roles

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        """What's the header text for this column?"""
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Called when user clicks a checkbox."""
        if not index.isValid():
            return False

        if index.column() == self.CHECKBOX_COL and role == Qt.CheckStateRole:
            tx_id = self._rows[index.row()].transaction.id
            if value == Qt.Checked:
                self._selected_ids.add(tx_id)
            else:
                self._selected_ids.discard(tx_id)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            self.checkbox_clicked.emit()
            return True
        return False

    def flags(self, index):
        """Tells Qt which cells are checkable, editable, selectable."""
        base_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if index.column() == self.CHECKBOX_COL and self._is_selection_mode:
            return base_flags | Qt.ItemIsUserCheckable

        return base_flags

    def _color_for_type(self, op_type, role=Qt.BackgroundRole):
        """Colors operation based on its type"""
        if role == Qt.ForegroundRole:
            return {
                OperationType.INCOME: self.INCOME_COLOR,
                OperationType.EXPENSE: self.EXPENSE_COLOR,
                OperationType.SAVING: self.SAVINGS_COLOR,
                OperationType.INVESTMENT: self.INVESTMENT_COLOR,
            }.get(op_type)
        return {
            OperationType.INCOME: self.BG_INCOME_COLOR,
            OperationType.EXPENSE: self.BG_EXPENSE_COLOR,
            OperationType.SAVING: self.BG_SAVINGS_COLOR,
            OperationType.INVESTMENT: self.BG_INVESTMENT_COLOR,
        }.get(op_type)

    # Set & reload methods
    def reload(self):
        """Reload table model data"""
        wallet_id = self._app_state.active_wallet_id

        if wallet_id is None:
            self.beginResetModel()
            self._rows = []
            self._total_count = 0
            self.endResetModel()

            return

        self.beginResetModel()
        self._rows = self._service.get_paginated_for_display(
            wallet_id=wallet_id,
            page=self._page,
            page_size=self._page_size,
            sort_by=self._sort_by,
            sort_order=self._sort_order,
            search=self._search,
        )
        self._total_count = self._service.get_count(
            wallet_id=wallet_id, search=self._search
        )
        self.endResetModel()

    def set_page(self, page: int):
        """Set current page"""
        self._page = page
        self._selected_ids = set()

        self.reload()

    def set_sort(self, column, order):
        """Set sorting"""
        self._sort_by = column
        self._sort_order = order
        self._page = 1
        self.reload()

    def set_search(self, query):
        """Set search query"""
        self._search = query
        self._page = 1

        self.reload()

    def set_selection_mode(self, enabled: bool):
        """Set selection mode"""
        self._is_selection_mode = enabled
        if not enabled:
            self._selected_ids.clear()
        self.beginResetModel()
        self.endResetModel()

    def select_all(self):
        """Select all displayed rows"""
        self._selected_ids = set()
        for row in self._rows:
            row_id = row.transaction.id

            if row_id not in self._selected_ids:
                self._selected_ids.add(row_id)
            else:
                self._selected_ids.discard(row_id)

        self._notify_checkbox_column_changed()

    def deselect_all(self):
        """Deselect all rows"""
        self._selected_ids = set()
        self._notify_checkbox_column_changed()

    def toggle_select_all(self):
        """Toggle select all"""
        if not self.all_selected():
            self.select_all()
        else:
            self.deselect_all()

    def _notify_checkbox_column_changed(self):
        """Tell view to re-query checkbox state for all rows."""
        if not self._rows:
            return
        top = self.index(0, self.CHECKBOX_COL)
        bottom = self.index(self.rowCount() - 1, self.CHECKBOX_COL)
        self.dataChanged.emit(top, bottom, [Qt.CheckStateRole])
        self.checkbox_clicked.emit()

    def all_selected(self):
        """Check if all rows are selected"""
        return len(self._selected_ids) == self.rowCount()

    def get_selected_ids(self) -> list[int]:
        """Get selected ids"""
        return list(self._selected_ids)

    def get_row_transaction(self, row: int):
        """Get tranasaction for row id"""
        if 0 <= row < len(self._rows):
            return self._rows[row].transaction
        return None

    def total_pages(self) -> int:
        """Get total pages count"""
        if self._total_count == 0:
            return 1
        return math.ceil(self._total_count / self._page_size)

    @property
    def current_page(self) -> int:
        return self._page

    @property
    def total_count(self) -> int:
        return self._total_count

    @property
    def is_selection_mode(self) -> int:
        return self._is_selection_mode

    @property
    def sort_by(self) -> str:
        return self._sort_by

    @property
    def sort_order(self) -> str:
        return self._sort_order
