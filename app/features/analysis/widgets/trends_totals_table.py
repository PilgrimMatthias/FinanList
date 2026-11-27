from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor

from app.core.theme.palette import Palette
from app.core.utils import format_balance
from ..service import AnalysisService, MonthTotals
from .chart_helpers import month_full


def format_rate(rate: float) -> str:
    """0.369 -> '36,9%'. Comma decimal, like every amount in the app."""
    return f"{rate * 100:.1f}%".replace(".", ",")


class TotalsTableModel(QAbstractTableModel):
    """One row per month: what came in, what went out, what was left.

    Savings and investments are not columns here - they are already inside
    Difference, and a row that shows all six numbers invites the reader to
    add them up and get the wrong answer. The tooltip breaks it down.
    """

    reloaded = Signal()

    COLUMNS = ["Month", "Income", "Expense", "Difference", "Savings %"]

    MONTH_COL = 0
    INCOME_COL = 1
    EXPENSE_COL = 2
    DIFFERENCE_COL = 3
    RATE_COL = 4

    def __init__(self, service: AnalysisService, app_state, parent=None):
        super().__init__(parent)
        self._service = service
        self._app_state = app_state
        self._rows: list[MonthTotals] = []
        self._current = None

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

        # The delegate needs to know which month is still being filled.
        if role == Qt.UserRole:
            return self._is_in_progress(row)

        if role == Qt.DisplayRole:
            if col == self.MONTH_COL:
                return month_full(row.year, row.month)
            if col == self.RATE_COL:
                rate = row.savings_rate
                # No income means no rate - not a rate of zero.
                return "—" if rate is None else format_rate(rate)
            return format_balance(self._value_for(row, col))

        if role == Qt.ToolTipRole:
            return self._tooltip_for(row, col)

        if role == Qt.TextAlignmentRole:
            if col == self.MONTH_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            return int(Qt.AlignVCenter | Qt.AlignRight)

        if role == Qt.ForegroundRole:
            if col in (self.DIFFERENCE_COL, self.RATE_COL):
                if col == self.RATE_COL and row.savings_rate is None:
                    return Palette.color("text_muted")
                # Only a loss is flagged. A row of green for every ordinary
                # month drowns the one month that went wrong.
                if row.difference < 0:
                    return Palette.color("danger")
                return Palette.color("text_primary")
            if self._is_in_progress(row):
                return Palette.color("text_secondary")

        return None

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        if role == Qt.TextAlignmentRole and orientation == Qt.Horizontal:
            if section == self.MONTH_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            return int(Qt.AlignVCenter | Qt.AlignRight)
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Internals
    def _value_for(self, row: MonthTotals, col: int) -> float:
        return {
            self.INCOME_COL: row.income,
            self.EXPENSE_COL: row.expenses,
            self.DIFFERENCE_COL: row.difference,
        }.get(col, 0.0)

    def _is_in_progress(self, row: MonthTotals) -> bool:
        """The last month of the range, when it is the month we are in.

        A half-finished month always looks like a good one - the income has
        landed and half the spending has not.
        """
        if self._current is None:
            return False
        return (row.year, row.month) == self._current

    def _tooltip_for(self, row: MonthTotals, col: int) -> str | None:
        if col == self.DIFFERENCE_COL:
            return (
                f"{format_balance(row.income)} in, "
                f"{format_balance(row.expenses)} spent, "
                f"{format_balance(row.savings)} saved, "
                f"{format_balance(row.investments)} invested"
            )
        if col == self.RATE_COL and row.savings_rate is None:
            return "No income this month, so there is no rate to show."
        if self._is_in_progress(row):
            return "This month is still in progress."
        return None

    # Set & reload methods
    def set_range(self, start, months: int, current=None):
        """Load a window. `current` is (year, month) of the live month."""
        self._current = current
        wallet_id = self._app_state.active_wallet_id

        self.beginResetModel()
        if wallet_id is None:
            self._rows = []
        else:
            self._rows = self._service.get_totals(
                wallet_id=wallet_id, start=start, months=months
            )
        self.endResetModel()

        self.reloaded.emit()

    def get_row(self, row: int) -> MonthTotals | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def footer_values(self) -> list[str]:
        """The pinned summary row, in the same column order."""
        if not self._rows:
            return ["No data", "", "", "", ""]

        income = sum(r.income for r in self._rows)
        expenses = sum(r.expenses for r in self._rows)
        difference = sum(r.difference for r in self._rows)
        rate = format_rate(difference / income) if income else "—"

        count = len(self._rows)

        return [
            f"{count} month" + ("" if count == 1 else "s"),
            format_balance(income),
            format_balance(expenses),
            format_balance(difference),
            rate,
        ]

    def footer_tones(self) -> list[str | None]:
        """Palette key per footer cell: the range's result, green or red."""
        if not self._rows:
            return [None] * len(self.COLUMNS)

        difference = sum(r.difference for r in self._rows)
        tone = "income_text" if difference >= 0 else "danger"
        return [None, None, None, tone, tone]

    @property
    def has_rows(self) -> bool:
        return bool(self._rows)
