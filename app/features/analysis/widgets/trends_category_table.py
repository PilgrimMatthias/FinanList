from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from app.core.theme.palette import Palette
from app.core.utils import format_balance
from ..service import AnalysisService, CategoryStats, OUTFLOW_TYPES


class CategoryTableModel(QAbstractTableModel):
    """Spend per category over the range, biggest first.

    Serves both Trends dimensions. "By category" lists main categories and
    drills down; "Inside category" lists one category's subcategories and
    does not. The columns are identical, so one model with a parent_id and
    a header word beats two models that would drift apart.
    """

    reloaded = Signal()

    COLUMNS = ["Category", "Total", "Monthly avg", "Min", "Max", "% of all", ""]

    NAME_COL = 0
    TOTAL_COL = 1
    AVG_COL = 2
    MIN_COL = 3
    MAX_COL = 4
    SHARE_COL = 5
    CHEVRON_COL = 6

    def __init__(self, service: AnalysisService, app_state, parent=None):
        super().__init__(parent)
        self._service = service
        self._app_state = app_state
        self._rows: list[CategoryStats] = []
        self._parent_id = None
        self._maximum = 0.0

    # QAbstractModel methods
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        col = index.column()

        # The bar delegate paints the Total column from this. The fraction
        # is of the LARGEST category, not of the whole - bars scaled to the
        # whole are all stubs as soon as there are more than a few rows.
        if role == Qt.UserRole and col == self.TOTAL_COL:
            fraction = row.total / self._maximum if self._maximum else 0.0
            return (fraction, row.color, format_balance(row.total))

        if role == Qt.DisplayRole:
            if col == self.NAME_COL:
                return row.name
            if col == self.SHARE_COL:
                return f"{row.share * 100:.1f}%"
            if col == self.CHEVRON_COL:
                return "›" if self.is_drilldown else ""
            if col == self.TOTAL_COL:
                # The delegate draws this, but DisplayRole keeps the value
                # copyable and keeps the column readable without it.
                return format_balance(row.total)
            return format_balance(self._value_for(row, col))

        if role == Qt.ToolTipRole:
            return self._tooltip_for(row, col)

        if role == Qt.TextAlignmentRole:
            if col == self.NAME_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            if col == self.CHEVRON_COL:
                return int(Qt.AlignVCenter | Qt.AlignHCenter)
            return int(Qt.AlignVCenter | Qt.AlignRight)

        if role == Qt.ForegroundRole:
            if col in (self.MIN_COL, self.MAX_COL, self.CHEVRON_COL):
                return Palette.color("text_muted")

        return None

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == self.NAME_COL:
                return "Category" if self.is_drilldown else "Subcategory"
            return self.COLUMNS[section]
        if role == Qt.TextAlignmentRole and orientation == Qt.Horizontal:
            if section == self.NAME_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            if section == self.CHEVRON_COL:
                return int(Qt.AlignVCenter | Qt.AlignHCenter)
            return int(Qt.AlignVCenter | Qt.AlignRight)
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Internals
    def _value_for(self, row: CategoryStats, col: int) -> float:
        return {
            self.TOTAL_COL: row.total,
            self.AVG_COL: row.monthly_avg,
            self.MIN_COL: row.minimum,
            self.MAX_COL: row.maximum,
        }.get(col, 0.0)

    def _tooltip_for(self, row: CategoryStats, col: int) -> str | None:
        if col == self.MIN_COL and row.minimum == 0.0:
            # A zero minimum is a fact about the range, not missing data.
            return "Nothing spent here in at least one month of the range."
        if col == self.AVG_COL:
            return "Total divided by every month in the range, not only the months with spending."
        if col == self.NAME_COL and self.is_drilldown:
            return "Open this category"
        return None

    # Set & reload methods
    def set_range(
        self,
        start,
        months: int,
        parent_id: int = None,
        operation_types: tuple = OUTFLOW_TYPES,
    ):
        """Load a window. `parent_id` switches to the subcategory view."""
        self._parent_id = parent_id
        wallet_id = self._app_state.active_wallet_id

        self.beginResetModel()
        if wallet_id is None:
            self._rows = []
        elif parent_id is None:
            self._rows = self._service.get_by_category(
                wallet_id=wallet_id,
                start=start,
                months=months,
                operation_types=operation_types,
            )
        else:
            self._rows = self._service.get_inside_category(
                wallet_id=wallet_id,
                parent_id=parent_id,
                start=start,
                months=months,
                operation_types=operation_types,
            )

        self._maximum = max((r.total for r in self._rows), default=0.0)
        self.endResetModel()

        self.reloaded.emit()

    def get_row(self, row: int) -> CategoryStats | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def footer_values(self) -> list[str]:
        """Min and Max are left blank on purpose.

        A total of the per-category minimums is not the minimum of
        anything - it would be a number with no meaning.
        """
        if not self._rows:
            return ["No data", "", "", "", "", "", ""]

        total = sum(r.total for r in self._rows)
        average = sum(r.monthly_avg for r in self._rows)

        return [
            "All categories" if self.is_drilldown else "All subcategories",
            format_balance(total),
            format_balance(average),
            "",
            "",
            "100,0%",
            "",
        ]

    @property
    def is_drilldown(self) -> bool:
        """True while listing main categories, which can be opened."""
        return self._parent_id is None

    @property
    def parent_id(self) -> int | None:
        return self._parent_id

    @property
    def has_rows(self) -> bool:
        return bool(self._rows)
