from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor, QFont

from app.core.app_state import AppState
from app.core.theme.palette import Palette
from ..service import AnalysisService
from ..forecast.forecast import ForecastMonth
from .chart_helpers import MONTHS_SHORT


def format_amount(value: float) -> str:
    """1 234,56 - space thousands, comma decimal."""
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


class ForecastTableModel(QAbstractTableModel):
    """One row per month of the projection."""

    recalculated = Signal()

    COLUMNS = [
        "Month",
        "Opening",
        "Income",
        "Expenses",
        "Savings",
        "Invest.",
        "Est. other",
        "Closing",
    ]
    MONTH_COL = 0
    OPENING_COL = 1
    INCOME_COL = 2
    EXPENSES_COL = 3
    SAVINGS_COL = 4
    INVESTMENTS_COL = 5
    EST_OTHER_COL = 6
    CLOSING_COL = 7

    AMOUNT_COLS = (1, 2, 3, 4, 5, 6, 7)

    def __init__(self, service: AnalysisService, app_state: AppState, parent=None):
        super().__init__(parent)
        self._service = service
        self._app_state = app_state
        self._rows: list[ForecastMonth] = []
        self._horizon = 6
        self._is_stale = False

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

        # UserRole carries what the delegates paint: the "to date" badge,
        # the over-plan marker and the floor label. Kept out of DisplayRole
        # so the text stays copyable and sortable.
        if role == Qt.UserRole:
            if col == self.MONTH_COL:
                return row.is_current_month
            if col == self.EST_OTHER_COL:
                return (row.over_plan_by, row.is_current_month)
            if col == self.CLOSING_COL:
                return (row.below_floor, row.floor_gap)
            return None

        if role == Qt.DisplayRole:
            if col == self.MONTH_COL:
                return f"{MONTHS_SHORT[row.month - 1]} {row.year}"
            return format_amount(self._value_for(row, col))

        if role == Qt.ToolTipRole:
            return self._tooltip_for(row, col)

        if role == Qt.TextAlignmentRole:
            if col == self.MONTH_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            return int(Qt.AlignVCenter | Qt.AlignRight)

        if role == Qt.FontRole:
            return self._font_for(col)

        if role == Qt.ForegroundRole:
            if col == self.CLOSING_COL and row.below_floor:
                return Palette.color("danger")
            if col == self.EST_OTHER_COL:
                # Estimated money is not committed money - italic and in
                # its own muted blue, like the dashed bar it stands for.
                return Palette.color("estimate_text")
            if col == self.OPENING_COL:
                # Opening is last month's closing - context, not news.
                return Palette.color("text_secondary")
            if col == self.MONTH_COL and row.is_current_month:
                return Palette.color("text_primary")

        if role == Qt.BackgroundRole and row.below_floor:
            # Copy: Palette.color() hands back the cached QColor itself, so
            # mutating it here would leave every red in the app at alpha 28
            # until the next theme switch rebuilt the cache.
            tint = QColor(Palette.color("danger"))
            tint.setAlpha(28)
            return tint

        return None

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        if role == Qt.TextAlignmentRole and orientation == Qt.Horizontal:
            if section == self.MONTH_COL:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
            return int(Qt.AlignVCenter | Qt.AlignRight)
        if orientation == Qt.Horizontal and section == self.EST_OTHER_COL:
            if role == Qt.FontRole:
                font = QFont()
                font.setItalic(True)
                font.setWeight(QFont.Weight.DemiBold)
                return font
            if role == Qt.ForegroundRole:
                return Palette.color("estimate_text")
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Internals
    def _font_for(self, col: int) -> QFont | None:
        """Month and Closing carry weight; Est. other is italic."""
        if col == self.EST_OTHER_COL:
            font = QFont()
            font.setItalic(True)
            return font
        if col == self.CLOSING_COL:
            font = QFont()
            font.setWeight(QFont.Weight.DemiBold)
            return font
        if col == self.MONTH_COL:
            font = QFont()
            font.setWeight(QFont.Weight.Medium)
            return font
        return None

    def _value_for(self, row: ForecastMonth, col: int) -> float:
        return {
            self.OPENING_COL: row.opening,
            self.INCOME_COL: row.income,
            self.EXPENSES_COL: row.expenses,
            self.SAVINGS_COL: row.savings,
            self.INVESTMENTS_COL: row.investments,
            self.EST_OTHER_COL: row.est_other,
            self.CLOSING_COL: row.closing,
        }[col]

    def _tooltip_for(self, row: ForecastMonth, col: int) -> str | None:
        """Explain the two cells whose number is not self-evident."""
        if col == self.EXPENSES_COL and row.actuals is not None:
            spent = row.actuals.expenses
            return (
                f"{format_amount(spent)} spent · "
                f"{format_amount(row.expenses - spent)} scheduled"
            )

        if col == self.EST_OTHER_COL and row.over_plan_by:
            if row.is_current_month:
                # Behaviour that already happened.
                return f"{format_amount(row.over_plan_by)} over your everyday plan"
            # Nothing has happened yet - this is a statement about the plan,
            # not about spending.
            return (
                f"Scheduled items exceed your plan by "
                f"{format_amount(row.over_plan_by)}"
            )

        if col == self.CLOSING_COL and row.below_floor:
            return f"{format_amount(row.floor_gap)} below your floor"

        return None

    # Set & reload methods
    def reload(self):
        """Recalculate the forecast. Button-driven, never automatic."""
        wallet_id = self._app_state.active_wallet_id

        self.beginResetModel()
        if wallet_id is None:
            self._rows = []
        else:
            self._rows = self._service.get_forecast(
                wallet_id=wallet_id, horizon=self._horizon
            )
        self.endResetModel()

        self._is_stale = False
        self.recalculated.emit()

    def mark_stale(self):
        """Transactions changed underneath us.

        Deliberately does NOT recalculate - redrawing the table under
        someone who is reading it is worse than showing a banner.
        """
        self._is_stale = True

    def set_horizon(self, horizon: int):
        self._horizon = horizon
        self.reload()

    def get_row(self, row: int) -> ForecastMonth | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    # Summary strip
    def summary(self) -> dict:
        """The three figures above the table.

        All three describe the current month, which is the only row anyone
        acts on.
        """
        current = next((r for r in self._rows if r.is_current_month), None)
        if current is None:
            return {"available": 0.0, "yet_to_pay": 0.0, "month_end": 0.0}

        actual = current.actuals
        scheduled_remaining = (
            (current.expenses - actual.expenses if actual else current.expenses)
            + (current.savings - actual.savings if actual else current.savings)
            + (
                current.investments - actual.investments
                if actual
                else current.investments
            )
        )

        return {
            "available": current.est_other,
            "yet_to_pay": scheduled_remaining,
            "month_end": current.closing,
            "over_plan_by": current.over_plan_by,
            "below_floor": current.below_floor,
            "floor_gap": current.floor_gap,
        }

    @property
    def is_stale(self) -> bool:
        return self._is_stale

    @property
    def horizon(self) -> int:
        return self._horizon

    @property
    def has_rows(self) -> bool:
        return bool(self._rows)
