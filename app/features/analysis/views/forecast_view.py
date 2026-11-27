from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QStackedWidget,
    QTableView,
    QAbstractItemView,
    QHeaderView,
)

from app.core import Frame, PushButton, SegmentedControl, show_error
from app.core.app_state import AppState
from app.core.utils import format_balance
from app.core.theme.palette import Palette, palette_signals

from ..service import AnalysisService
from ..widgets.forecast_table import ForecastTableModel
from ..widgets.forecast_chart import ForecastChart
from ..widgets.summary_tile import SummaryTile
from ..widgets.chart_legend import (
    ChartLegend,
    SQUARE,
    DASHED_SQUARE,
    LINE,
    DASHED_LINE,
)
from ..widgets.scheduled_popover import ScheduledPopover
from ..widgets.forecast_delegates import (
    ToDateBadgeDelegate,
    OverPlanDelegate,
    BelowFloorDelegate,
)

HORIZONS = [(3, "3 mo"), (6, "6 mo"), (12, "12 mo")]
DEFAULT_HORIZON = 6
ROW_HEIGHT = 38
NOTE_ROW_HEIGHT = 50

LEGEND = [
    ("Expenses", "chart_expense", SQUARE),
    ("Savings", "chart_saving", SQUARE),
    ("Investments", "chart_investment", SQUARE),
    ("Est. other", "chart_estimate", DASHED_SQUARE),
    ("Balance", "chart_balance", LINE),
    ("Floor", "chart_floor", DASHED_LINE),
]


class ForecastView(QWidget):
    """Projection for the active wallet: summary, chart, assumptions, table."""

    edit_assumptions_requested = Signal()

    def __init__(
        self,
        service: AnalysisService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.app_state = app_state

        self._calculated_at = None
        self._has_calculated = False
        self._assumptions = None

        self._init_view()

        self.app_state.wallet_changed.connect(self._on_wallet_changed)
        self.app_state.transaction_changed.connect(self._mark_stale)
        self.app_state.recurring_transaction_changed.connect(self._mark_stale)

        palette_signals.changed.connect(self._on_palette_changed)

    def _init_view(self):
        "Initialize view"
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(0)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(0, 5, 0, 0)

        main_layout.addWidget(self._build_stale_banner())
        main_layout.addWidget(self._build_controls())
        main_layout.addWidget(self._build_states())

    def _build_stale_banner(self) -> QWidget:
        """Shown when transactions changed after the last calculation."""
        self.stale_banner = QFrame(self)
        self.stale_banner.setObjectName("staleBanner")
        self.stale_banner.hide()

        banner_layout = QHBoxLayout(self.stale_banner)
        banner_layout.setContentsMargins(12, 8, 12, 8)
        banner_layout.setSpacing(10)

        dot = QLabel("●", self.stale_banner)
        dot.setObjectName("staleBannerDot")

        message = QLabel(
            "Transactions changed since this forecast was calculated.",
            self.stale_banner,
        )
        message.setObjectName("staleBannerText")

        recalculate = PushButton(
            text="Recalculate",
            object_name="linkButton",
            width=90,
            height=24,
            font_size=9,
            on_click=self._on_calculate,
        )

        banner_layout.addWidget(dot)
        banner_layout.addWidget(message)
        banner_layout.addStretch()
        banner_layout.addWidget(recalculate)

        return self.stale_banner

    def _build_controls(self) -> QWidget:
        """Horizon selector, last-calculated time, Calculate."""
        controls = Frame(self, add_stylesheet=False)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)

        self.horizon_control = SegmentedControl(
            parent=controls,
            text="Horizon",
            values=HORIZONS,
            default_value=DEFAULT_HORIZON,
            label_position="left",
            on_change=self._on_horizon_changed,
        )

        self.horizon_control.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        self.calculated_label = QLabel("Not calculated yet", controls)
        self.calculated_label.setObjectName("forecastTimestamp")

        self.calculate_btn = PushButton(
            text="Calculate",
            width=120,
            height=32,
            font_size=9,
            on_click=self._on_calculate,
        )

        controls_layout.addWidget(self.horizon_control)
        controls_layout.addStretch()
        controls_layout.addWidget(self.calculated_label)
        controls_layout.addWidget(self.calculate_btn)

        return controls

    def _build_states(self) -> QWidget:
        """Content page and empty-state page."""
        self.stacked_states = QStackedWidget(self)
        self.stacked_states.addWidget(self._build_content())
        self.stacked_states.addWidget(self._build_empty_state())
        return self.stacked_states

    def _build_content(self) -> QWidget:
        """Build content page: summary, chart, assumptions, table."""
        page = QScrollArea(self)
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.Shape.NoFrame)
        page.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(12)

        inner_layout.addWidget(self._build_summary())
        inner_layout.addWidget(self._build_chart_card())
        inner_layout.addWidget(self._build_assumptions())
        inner_layout.addWidget(self._build_table())
        inner_layout.addStretch()

        page.setWidget(inner)
        return page

    def _build_summary(self) -> QWidget:
        """Build summary row"""
        strip = QFrame(self)
        strip.setObjectName("summaryStrip")
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        strip_layout.setSpacing(0)

        self.available_tile = SummaryTile(
            strip, text="Available to spend", value="0,00"
        )
        self.yet_to_pay_tile = SummaryTile(
            strip,
            text="Yet to pay this month",
            value="0,00",
            hint_is_link=True,
            highlight=True,
        )
        self.month_end_tile = SummaryTile(
            strip, text="Projected month end", value="0,00"
        )
        self.month_end_tile.setProperty("last", "true")

        self.yet_to_pay_tile.hint_clicked.connect(self._show_scheduled_popover)

        for tile in (
            self.available_tile,
            self.yet_to_pay_tile,
            self.month_end_tile,
        ):
            strip_layout.addWidget(tile, stretch=1)

        return strip

    def _build_chart_card(self) -> QWidget:
        """Build charts card"""
        card = QFrame(self)
        card.setObjectName("analysisCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 12)
        card_layout.setSpacing(10)

        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        legend = ChartLegend(card, title="Cash flow and balance", items=LEGEND)

        self.chart = ForecastChart(parent=card, height=260)

        card_layout.addWidget(legend)
        card_layout.addWidget(self.chart)

        return card

    def _build_assumptions(self) -> QWidget:
        """What the projection was built from, and a way to change it."""
        strip = QFrame(self)
        strip.setObjectName("assumptionsStrip")

        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(14, 9, 14, 9)
        strip_layout.setSpacing(18)

        heading = QLabel("Assumptions", strip)
        heading.setObjectName("assumptionsHeading")

        self.assumption_labels = {}
        for key in ("income", "everyday", "floor"):
            label = QLabel(strip)
            label.setObjectName("assumptionItem")
            label.setTextFormat(Qt.TextFormat.RichText)
            self.assumption_labels[key] = label

        edit = PushButton(
            text="Edit assumptions",
            object_name="linkButton",
            width=120,
            height=24,
            font_size=9,
            on_click=self.edit_assumptions_requested.emit,
        )

        strip_layout.addWidget(heading)
        for label in self.assumption_labels.values():
            strip_layout.addWidget(label)
        strip_layout.addStretch()
        strip_layout.addWidget(edit)

        return strip

    def _build_table(self) -> QWidget:
        card = QFrame(self)
        card.setObjectName("analysisCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.forecast_table_model = ForecastTableModel(
            service=self.service, app_state=self.app_state
        )
        self.forecast_table_model.recalculated.connect(self._on_recalculated)

        self.forecast_table = QTableView(card)
        self.forecast_table.setModel(self.forecast_table_model)
        self.forecast_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.forecast_table.setShowGrid(False)
        self.forecast_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.forecast_table.verticalHeader().hide()
        self.forecast_table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
        self.forecast_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.forecast_table.horizontalHeader().setSortIndicatorShown(False)

        self.forecast_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.forecast_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Month (with its badge) and the bold Closing figure size to their
        # content; the plain numbers share what is left. An even split
        # wraps "10 463,55" onto two lines at 800px.
        for column in (
            self.forecast_table_model.MONTH_COL,
            self.forecast_table_model.CLOSING_COL,
        ):
            self.forecast_table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeToContents
            )
        self.forecast_table.setWordWrap(False)

        # Delegates read everything they paint from Qt.UserRole, so the
        # model stays the only thing that decides when a flag applies.
        self._to_date_delegate = ToDateBadgeDelegate()
        self._over_plan_delegate = OverPlanDelegate()
        self._floor_delegate = BelowFloorDelegate()

        self.forecast_table.setItemDelegateForColumn(
            self.forecast_table_model.MONTH_COL, self._to_date_delegate
        )
        self.forecast_table.setItemDelegateForColumn(
            self.forecast_table_model.EST_OTHER_COL, self._over_plan_delegate
        )
        self.forecast_table.setItemDelegateForColumn(
            self.forecast_table_model.CLOSING_COL, self._floor_delegate
        )

        card_layout.addWidget(self.forecast_table)
        return card

    def _build_empty_state(self) -> QWidget:
        """Empty state"""
        empty = QWidget(self)
        empty_layout = QVBoxLayout(empty)
        empty_layout.setContentsMargins(0, 0, 0, 0)
        empty_layout.setSpacing(10)

        self.empty_top_label = QLabel(empty)
        self.empty_top_label.setObjectName("not_tr_label")
        self.empty_top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.empty_bottom_label = QLabel(empty)
        self.empty_bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_bottom_label.setWordWrap(True)

        self.empty_action_btn = PushButton(
            text="Set up the plan",
            width=140,
            height=32,
            font_size=9,
            on_click=self.edit_assumptions_requested.emit,
        )

        empty_layout.addStretch()
        empty_layout.addWidget(self.empty_top_label)
        empty_layout.addWidget(self.empty_bottom_label)
        empty_layout.addWidget(
            self.empty_action_btn, alignment=Qt.AlignmentFlag.AlignCenter
        )
        empty_layout.addStretch()

        return empty

    # RELOAD
    def reload(self):
        """Recalculate and repaint everything."""
        wallet_id = self.app_state.active_wallet_id
        if wallet_id is None:
            self._show_empty_state(
                "No wallet selected.",
                "Pick a wallet to see its forecast.",
                show_action=False,
            )
            return

        assumptions = self.service.get_assumptions(wallet_id=wallet_id)
        self._update_assumptions(assumptions)

        if not assumptions.is_complete:
            self._show_empty_state(
                "Your monthly plan isn't set.",
                "A forecast needs planned income and everyday spending on "
                "this wallet. Add them and the projection appears here.",
            )
            return

        try:
            self.forecast_table_model.reload()
        except Exception as error:
            print(error)
            import traceback

            traceback.print_exc()
            show_error(self, str(error), title="Forecast error")
            return

        self.stacked_states.setCurrentIndex(0)
        self._update_ui()

    def _update_ui(self):
        """Repaint summary, chart and table geometry from the model."""
        self._update_summary()

        rows = [
            self.forecast_table_model.get_row(index)
            for index in range(self.forecast_table_model.rowCount())
        ]
        self.chart.set_rows(rows, floor=self._floor)
        self._fit_table_height()
        self._update_stale_banner()

    def _update_summary(self):
        summary = self.forecast_table_model.summary()

        over_plan = summary.get("over_plan_by")
        self.available_tile.set_value(format_balance(summary["available"]))
        self.available_tile.set_hint(
            f"{format_balance(over_plan)} over plan this month" if over_plan else None,
            tone="warning",
        )

        self.yet_to_pay_tile.set_value(format_balance(summary["yet_to_pay"]))
        self.yet_to_pay_tile.set_hint(
            f"{self._scheduled_count()} scheduled · details ▾", tone="accent"
        )

        below_floor = summary.get("below_floor")
        self.month_end_tile.set_value(
            format_balance(summary["month_end"]),
            tone="danger" if below_floor else None,
        )
        self.month_end_tile.set_hint(
            (
                f"{format_balance(summary['floor_gap'])} below floor "
                f"({format_balance(self._floor)})"
                if below_floor
                else None
            ),
            tone="danger",
        )

    def _update_assumptions(self, assumptions):
        """Keep the strip truthful even when the plan is incomplete."""
        self._assumptions = assumptions
        self._floor = assumptions.floor

        value_colour = Palette.hex("text_primary")

        def shown(caption, value):
            text = format_balance(value) if value is not None else "not set"
            return (
                f"{caption} <span style='color:{value_colour}; font-weight:600'>"
                f"{text}</span>"
            )

        self.assumption_labels["income"].setText(
            shown("Income", assumptions.planned_income)
        )
        self.assumption_labels["everyday"].setText(
            shown("Everyday", assumptions.planned_everyday)
        )
        self.assumption_labels["floor"].setText(shown("Floor", assumptions.floor))

    def _fit_table_height(self):
        """Size the table to its rows so the page owns the only scrollbar."""
        for index in range(self.forecast_table_model.rowCount()):
            row = self.forecast_table_model.get_row(index)
            has_note = bool(row.over_plan_by) or bool(row.below_floor)
            self.forecast_table.setRowHeight(
                index, NOTE_ROW_HEIGHT if has_note else ROW_HEIGHT
            )

        header = self.forecast_table.horizontalHeader().height()
        rows = self.forecast_table.verticalHeader().length()
        self.forecast_table.setFixedHeight(header + rows + 2)

    def _update_stale_banner(self):
        self.stale_banner.setVisible(self.forecast_table_model.is_stale)

    def _show_empty_state(self, top: str, bottom: str, show_action=True):
        self.empty_top_label.setText(top)
        self.empty_bottom_label.setText(bottom)
        self.empty_action_btn.setVisible(show_action)
        self.stacked_states.setCurrentIndex(1)

    def _scheduled_count(self) -> int:
        """Number of unconfirmed occurrences left in the current month."""
        return len(self._remaining_occurrences())

    def _remaining_occurrences(self) -> list:
        wallet_id = self.app_state.active_wallet_id
        if wallet_id is None:
            return []

        today = datetime.today()
        next_month = datetime(
            today.year + (today.month == 12),
            1 if today.month == 12 else today.month + 1,
            1,
        )
        return self.service.get_scheduled_occurrences(
            wallet_id=wallet_id, end=next_month
        )

    # EVENTS
    def showEvent(self, event):
        """Calculate once, the first time the tab is actually looked at."""
        super().showEvent(event)
        if not self._has_calculated:
            self._has_calculated = True
            self.reload()
        else:
            # "today" goes stale overnight when the app stays open.
            self._update_timestamp()

    def _on_calculate(self):
        self.reload()

    def _on_horizon_changed(self, horizon: int):
        """Horizon is a different question - answer it straight away."""
        self.forecast_table_model.set_horizon(horizon)
        self.stacked_states.setCurrentIndex(0)
        self._update_ui()

    def _on_wallet_changed(self, wallet_id: int = None):
        """Plan, balance and schedule all change - nothing survives."""
        if not self._has_calculated:
            return
        self.reload()

    def _on_recalculated(self):
        self._calculated_at = datetime.now()
        self._update_timestamp()

    def _update_timestamp(self):
        """'Calculated today, 14:02' - or the date, once that is no longer true."""
        if self._calculated_at is None:
            return
        when = self._calculated_at
        day = (
            "today"
            if when.date() == datetime.today().date()
            else when.strftime("%d.%m")
        )
        self.calculated_label.setText(f"Calculated {day}, {when.strftime('%H:%M')}")

    def _on_palette_changed(self, *args):
        if self._assumptions is not None:
            self._update_assumptions(self._assumptions)

    def _mark_stale(self, *args):
        """Raise the banner. Deliberately does not recalculate."""
        if not self._has_calculated:
            return
        self.forecast_table_model.mark_stale()
        self._update_stale_banner()

    def _show_scheduled_popover(self):
        popover = ScheduledPopover(self, occurrences=self._remaining_occurrences())
        popover.show_under(self.yet_to_pay_tile)
