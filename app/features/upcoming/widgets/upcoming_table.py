import math
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor
from ..service import UpcomingService
from app.core.app_state import AppState
from ..models import RecurringTransactionDisplay
from PySide6.QtCore import Qt

from app.core.enums import OperationType
from app.core.utils import cast_date_to_proper_format


class UpcomingTableModel(QAbstractTableModel):
    checkbox_clicked = Signal()

    COLUMNS = ["", "Name", "Interval", "Next Due", "Category", "Amount", "Active"]
    CHECKBOX_COL = 0
    CATEGORY_COL = 4
    ACTIVE_COL = 6

    INCOME_COLOR = QColor("#008000")
    EXPENSE_COLOR = QColor("#ff3333")
    SAVINGS_COLOR = QColor("#1e65c8")
    INVESTMENT_COLOR = QColor("#0f1f70")

    BG_INCOME_COLOR = QColor("#b3ffb3")
    BG_EXPENSE_COLOR = QColor("#ffcccc")
    BG_SAVINGS_COLOR = QColor("#bcc5f6")
    BG_INVESTMENT_COLOR = QColor("#bdd4f5")

    def __init__(self, service: UpcomingService, app_state: AppState, parent=None):
        super().__init__(parent)
        self._service = service
        self._app_state = app_state
        self._rows: list[RecurringTransactionDisplay] = []
        self._total_count = 0
        self._page = 1
        self._page_size = 100
        self._sort_by = "next_due_date"
        self._sort_order = "ASC"
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
                    if row.recurring.id in self._selected_ids
                    else Qt.Unchecked
                )
            return None  # No display text in checkbox column

        # Category col setting
        if col == self.CATEGORY_COL:
            if role == Qt.UserRole:
                return (
                    row.recurring.is_active,
                    row.sub_category_color,
                    f"{row.main_category_name} / {row.sub_category_name}",
                )
            if role == Qt.DisplayRole:
                return ""
            return None
        
        # Active col setting
        if col == self.ACTIVE_COL:
            if role == Qt.UserRole:
                return (row.recurring.is_active, row.recurring.id)
            if role == Qt.DisplayRole:
                return ""
            return None

        # Remaining display roles
        if role == Qt.DisplayRole:
            # The text shown in the cell
            if col == 1:
                return row.recurring.title
            if col == 5:
                amount = row.recurring.amount
                op_type = row.recurring.operation_type
                sign = "+" if op_type == OperationType.INCOME else "-"
                return f"{sign}{amount:,.2f}".replace(",", " ").replace(".", ",")
            if col == 2:
                return row.recurring.recurrence_interval
            if col == 3:
                if not row.recurring.is_active: 
                    return "-"
                if row.is_overdue:
                    return "{0} (overdue)".format(cast_date_to_proper_format(row.recurring.next_due_date))
                
                return cast_date_to_proper_format(row.recurring.next_due_date)

        if role == Qt.TextAlignmentRole:
            if col in [
                1,
                2,
            ]:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            else:
                return int(Qt.AlignCenter)

        if role == Qt.ForegroundRole:
            if not row.recurring.is_active and col in [1,2,3,4,5]:
                return QColor("#808080")
            if col == 3 and row.is_overdue:
                return QColor("#ff3333")
            if col == 5:
                return self._color_for_type(
                    row.recurring.operation_type, role=Qt.ForegroundRole
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
            tx_id = self._rows[index.row()].recurring.id
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
        self._selected_ids = {row.recurring.id for row in self._rows}
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

    def get_row_recurring(self, row: int):
        """Get tranasaction for row id"""
        if 0 <= row < len(self._rows):
            return self._rows[row].recurring
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
    def is_selection_mode(self) -> bool:
        return self._is_selection_mode

    @property
    def sort_by(self) -> str:
        return self._sort_by

    @property
    def sort_order(self) -> str:
        return self._sort_order
