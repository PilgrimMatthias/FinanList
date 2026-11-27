from datetime import date

from PySide6.QtCore import Qt, QTimer
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

from app.core import Frame, PushButton, ComboBox, SegmentedControl
from app.core.app_state import AppState
from app.core.utils import shift_month, format_balance

from ..service import AnalysisService, CategoryStats, OUTFLOW_TYPES, month_range
from ..widgets.trends_totals_table import TotalsTableModel
from ..widgets.trends_category_table import CategoryTableModel
from ..widgets.trends_charts import TotalsChart, CategoryChart
from ..widgets.category_bar_delegate import CategoryBarDelegate
from ..widgets.table_footer import TableFooter
from ..widgets.chart_legend import ChartLegend, SQUARE

TOTALS = "totals"
BY_CATEGORY = "by_category"
INSIDE_CATEGORY = "inside_category"

DIMENSIONS = [
    (TOTALS, "Totals"),
    (BY_CATEGORY, "By category"),
    (INSIDE_CATEGORY, "Inside category"),
]

PICKER_MONTHS = 36
DEFAULT_RANGE = 12
RELOAD_DELAY_MS = 150
ROW_HEIGHT = 40
MAX_VISIBLE_ROWS = 12

TOTALS_LEGEND = [
    ("Income", "chart_income", SQUARE),
    ("Expense", "chart_expense", SQUARE),
]
IN_PROGRESS_NOTE = "* month in progress"


class TrendsView(QWidget):
    """Where the money actually went, over a range the user picks."""

    def __init__(
        self,
        service: AnalysisService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.app_state = app_state

        self._dimension = TOTALS
        self._parent_id = None
        self._parent_name = None
        self._has_loaded = False

        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(RELOAD_DELAY_MS)
        self._reload_timer.timeout.connect(self.reload)

        self._init_view()

        self.app_state.wallet_changed.connect(self._on_wallet_changed)
        self.app_state.transaction_changed.connect(self._schedule_reload)

    # VIEW
    def _init_view(self):
        "Initialize view"
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(0)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(0, 5, 0, 0)

        main_layout.addWidget(self._build_controls())
        main_layout.addWidget(self._build_breadcrumb())
        main_layout.addWidget(self._build_states())

    def _build_controls(self) -> QWidget:
        """Range pickers on the left, dimension switch on the right."""
        controls = Frame(self, add_stylesheet=False)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)

        months = self._picker_months()

        self.from_box = ComboBox(
            values=months,
            text="From",
            default_value=months[-DEFAULT_RANGE][1],
            label_position="left",
            on_change=self._on_range_changed,
        )
        self.to_box = ComboBox(
            values=months,
            text="to",
            default_value=months[-1][1],
            label_position="left",
            on_change=self._on_range_changed,
        )

        self.dimension_control = SegmentedControl(
            parent=controls,
            values=DIMENSIONS,
            default_value=TOTALS,
            label_position="left",
            on_change=self._on_dimension_changed,
        )

        self.dimension_control.set_enabled_values([TOTALS, BY_CATEGORY])

        self.range_error = QLabel(controls)
        self.range_error.setObjectName("rangeError")
        self.range_error.hide()

        controls_layout.addWidget(self.from_box)
        controls_layout.addWidget(self.to_box)
        controls_layout.addWidget(self.range_error)
        controls_layout.addStretch()
        controls_layout.addWidget(self.dimension_control)

        return controls

    def _build_breadcrumb(self) -> QWidget:
        """Only shown inside a category - the way back out."""
        self.breadcrumb = Frame(self, add_stylesheet=False)
        breadcrumb_layout = QHBoxLayout(self.breadcrumb)
        breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        breadcrumb_layout.setSpacing(8)

        self.breadcrumb_label = QLabel(self.breadcrumb)
        self.breadcrumb_label.setObjectName("breadcrumbLabel")

        back = PushButton(
            text="← All categories",
            object_name="linkButton",
            width=120,
            height=24,
            font_size=9,
            on_click=self._on_back_to_categories,
        )

        breadcrumb_layout.addWidget(back)
        breadcrumb_layout.addWidget(self.breadcrumb_label)
        breadcrumb_layout.addStretch()

        self.breadcrumb.hide()
        return self.breadcrumb

    def _build_states(self) -> QWidget:
        self.stacked_states = QStackedWidget(self)
        self.stacked_states.addWidget(self._build_content())
        self.stacked_states.addWidget(self._build_empty_state())
        return self.stacked_states

    def _build_content(self) -> QWidget:
        page = QScrollArea(self)
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.Shape.NoFrame)
        page.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(12)

        inner_layout.addWidget(self._build_chart_card())

        table_block = QVBoxLayout()
        table_block.setContentsMargins(0, 0, 0, 0)
        table_block.setSpacing(8)
        table_block.addWidget(self._build_table())
        table_block.addWidget(self._build_footer())
        inner_layout.addLayout(table_block)
        inner_layout.addStretch()

        page.setWidget(inner)
        return page

    def _build_chart_card(self) -> QWidget:
        self.chart_card = QFrame(self)
        self.chart_card.setObjectName("analysisCard")

        card_layout = QVBoxLayout(self.chart_card)
        card_layout.setContentsMargins(16, 14, 16, 12)
        card_layout.setSpacing(10)

        self.chart_card.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )

        self.chart_legend = ChartLegend(self.chart_card, title="Monthly cash flow")

        self.totals_chart = TotalsChart(parent=self.chart_card, height=220)
        self.category_chart = CategoryChart(parent=self.chart_card, height=200)
        self.category_chart.hide()

        card_layout.addWidget(self.chart_legend)
        card_layout.addWidget(self.totals_chart)
        card_layout.addWidget(self.category_chart)

        return self.chart_card

    def _build_table(self) -> QWidget:
        card = QFrame(self)
        card.setObjectName("analysisCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.totals_model = TotalsTableModel(
            service=self.service, app_state=self.app_state
        )
        self.category_model = CategoryTableModel(
            service=self.service, app_state=self.app_state
        )

        self.table = QTableView(card)
        self.table.setModel(self.totals_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSortIndicatorShown(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.clicked.connect(self._on_row_clicked)

        self._bar_delegate = CategoryBarDelegate()

        card_layout.addWidget(self.table)
        return card

    def _build_footer(self) -> QWidget:
        self.footer = TableFooter(self)
        self.footer.follow(self.table)
        return self.footer

    def _build_empty_state(self) -> QWidget:
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

        empty_layout.addStretch()
        empty_layout.addWidget(self.empty_top_label)
        empty_layout.addWidget(self.empty_bottom_label)
        empty_layout.addStretch()

        return empty

    def reload(self):
        """Query and repaint for the current range and dimension."""
        self._reload_timer.stop()

        if self.app_state.active_wallet_id is None:
            self._show_empty_state(
                "No wallet selected.", "Pick a wallet to see its trends."
            )
            return

        window = self._range()
        if window is None:
            self._show_empty_state(
                "That range runs backwards.",
                "The first month has to come before the last one.",
            )
            return

        start, months = window

        if self._dimension == TOTALS:
            self._load_totals(start, months)
        else:
            self._load_categories(start, months)

        self._has_loaded = True

    def _load_totals(self, start: date, months: int):
        self.totals_model.set_range(
            start=start, months=months, current=self._current_month()
        )

        self._use_model(self.totals_model)

        if not self.totals_model.has_rows:
            self._show_no_data()
            return

        rows = [
            self.totals_model.get_row(index)
            for index in range(self.totals_model.rowCount())
        ]
        self.totals_chart.set_rows(rows, current=self._current_month())
        self.chart_legend.set_title("Monthly cash flow")
        self.chart_legend.set_items(TOTALS_LEGEND)
        self.chart_legend.set_note(
            IN_PROGRESS_NOTE if self.totals_chart.has_in_progress() else None
        )
        self._show_chart(self.totals_chart)
        self._finish(self.totals_model)

    def _load_categories(self, start: date, months: int):
        parent_id = self._parent_id if self._dimension == INSIDE_CATEGORY else None

        self.category_model.set_range(
            start=start,
            months=months,
            parent_id=parent_id,
            operation_types=OUTFLOW_TYPES,
        )

        self._use_model(self.category_model)

        if not self.category_model.has_rows:
            self._show_no_data()
            return

        if self._dimension == BY_CATEGORY:
            self.chart_card.hide()
        else:
            series = self._parent_series(months)
            # The dashed line has no legend, so the title names it.
            self.chart_legend.set_title(
                f"{series.name} by month · average "
                f"{format_balance(series.monthly_avg)}"
            )
            self.chart_legend.set_items([])
            self.chart_legend.set_note(None)
            self.category_chart.set_stats(
                series,
                months=month_range(start, months),
            )
            self._show_chart(self.category_chart)

        self._finish(self.category_model)

    def _parent_series(self, months: int) -> CategoryStats:
        """The parent category month by month, summed from its children."""
        rows = [
            self.category_model.get_row(index)
            for index in range(self.category_model.rowCount())
        ]
        monthly = [sum(values) for values in zip(*(r.monthly for r in rows))]
        total = sum(monthly)

        return CategoryStats(
            category_id=self._parent_id,
            name=self._parent_name or "",
            color=rows[0].color if rows else None,
            total=total,
            monthly_avg=total / months if months else 0.0,
            minimum=min(monthly, default=0.0),
            maximum=max(monthly, default=0.0),
            share=1.0,
            monthly=monthly,
        )

    def _use_model(self, model):
        """Swap the model and the per-column decoration that goes with it."""
        if self.table.model() is not model:
            self.table.setModel(model)
            self.table.clearSelection()

        is_category = model is self.category_model

        self.table.setItemDelegateForColumn(
            self.category_model.TOTAL_COL,
            self._bar_delegate if is_category else None,
        )
        self.table.setColumnHidden(
            self.category_model.CHEVRON_COL,
            not (is_category and model.is_drilldown),
        )
        self.footer.set_column_hidden(
            self.category_model.CHEVRON_COL,
            not (is_category and model.is_drilldown),
        )

        self._apply_column_sizing(is_category)

    def _apply_column_sizing(self, is_category: bool):
        """Totals shares the width evenly; the category table does not."""
        header = self.table.horizontalHeader()

        if not is_category:
            header.setSectionResizeMode(QHeaderView.Stretch)
            return

        for column in range(self.category_model.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(self.category_model.NAME_COL, QHeaderView.Stretch)
        header.setSectionResizeMode(self.category_model.TOTAL_COL, QHeaderView.Stretch)
        header.setSectionResizeMode(self.category_model.CHEVRON_COL, QHeaderView.Fixed)
        self.table.setColumnWidth(self.category_model.CHEVRON_COL, 28)

    def _fit_columns_to_footer(self):
        """Widen any content-sized column the bold footer would not fit."""
        header = self.table.horizontalHeader()
        skip = (
            self.category_model.NAME_COL,
            self.category_model.TOTAL_COL,
            self.category_model.CHEVRON_COL,
        )
        for column in range(self.category_model.columnCount()):
            if column in skip:
                continue
            needed = self.footer.content_width(column)
            # The hint, not sectionSize: right after a model reset the
            # section has not been re-measured yet.
            current = max(
                self.table.sizeHintForColumn(column), header.sectionSizeHint(column)
            )
            if needed > current:
                header.setSectionResizeMode(column, QHeaderView.Fixed)
                self.table.setColumnWidth(column, needed)

    def _finish(self, model):
        self.stacked_states.setCurrentIndex(0)
        tones = model.footer_tones() if hasattr(model, "footer_tones") else None
        self.footer.set_values(model.footer_values(), tones=tones)
        if model is self.category_model:
            self._fit_columns_to_footer()
        self._fit_table_height(model)
        self.breadcrumb.setVisible(self._dimension == INSIDE_CATEGORY)
        if self._dimension == INSIDE_CATEGORY:
            self.breadcrumb_label.setText(self._parent_name or "")

    def _show_chart(self, chart):
        self.chart_card.show()
        self.totals_chart.setVisible(chart is self.totals_chart)
        self.category_chart.setVisible(chart is self.category_chart)

    def _fit_table_height(self, model):
        """Short lists size to their rows; long ones get their own scroll."""
        rows = model.rowCount()
        header = self.table.horizontalHeader().height()

        if rows <= MAX_VISIBLE_ROWS:
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.table.setFixedHeight(header + rows * ROW_HEIGHT + 2)
        else:
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.table.setFixedHeight(header + MAX_VISIBLE_ROWS * ROW_HEIGHT + 2)

    def _show_no_data(self):
        self._show_empty_state(
            "Nothing in this range.",
            "No transactions fall between the months you picked.",
        )

    def _show_empty_state(self, top: str, bottom: str):
        self.empty_top_label.setText(top)
        self.empty_bottom_label.setText(bottom)
        self.stacked_states.setCurrentIndex(1)

    # RANGE
    def _picker_months(self) -> list:
        """(data, text) for the last PICKER_MONTHS months, oldest first."""
        today = date.today()
        first_year, first_month = shift_month(
            today.year, today.month, -(PICKER_MONTHS - 1)
        )
        return [
            [f"{year:04d}-{month:02d}", f"{month:02d}.{year}"]
            for year, month in month_range(
                date(first_year, first_month, 1), PICKER_MONTHS
            )
        ]

    def _range(self) -> tuple[date, int] | None:
        """(start, month count) from the pickers, or None if inverted."""
        start = self._parse(self.from_box.get_data())
        end = self._parse(self.to_box.get_data())

        if start is None or end is None:
            return None

        months = (end.year - start.year) * 12 + (end.month - start.month) + 1
        if months < 1:
            self.range_error.setText("End month is before the start month.")
            self.range_error.show()
            return None

        self.range_error.hide()
        return start, months

    @staticmethod
    def _parse(value: str) -> date | None:
        if not value:
            return None
        year, month = value.split("-")
        return date(int(year), int(month), 1)

    @staticmethod
    def _current_month() -> tuple[int, int]:
        today = date.today()
        return today.year, today.month

    # EVENTS
    def showEvent(self, event):
        super().showEvent(event)
        if not self._has_loaded:
            self.reload()

    def _schedule_reload(self, *args):
        """Restart the debounce. Two picker changes become one query."""
        if not self._has_loaded:
            return
        self._reload_timer.start()

    def _on_range_changed(self, *args):
        self._schedule_reload()

    def _on_dimension_changed(self, dimension: str):
        self._dimension = dimension
        self.reload()

    def _on_wallet_changed(self, wallet_id: int = None):
        # The old category id means nothing in another wallet.
        self._reset_drilldown()
        if self._has_loaded:
            self.reload()

    def _on_row_clicked(self, index):
        """Click a main category to open it."""
        if self.table.model() is not self.category_model:
            return
        if not self.category_model.is_drilldown:
            return

        row = self.category_model.get_row(index.row())
        if row is None:
            return

        self._parent_id = row.category_id
        self._parent_name = row.name
        self._dimension = INSIDE_CATEGORY

        self.dimension_control.set_enabled_values(
            [TOTALS, BY_CATEGORY, INSIDE_CATEGORY]
        )
        self.dimension_control.set_data(INSIDE_CATEGORY)
        self.reload()

    def _on_back_to_categories(self):
        self._dimension = BY_CATEGORY
        self.dimension_control.set_data(BY_CATEGORY)
        self.reload()

    def _reset_drilldown(self):
        self._parent_id = None
        self._parent_name = None
        if self._dimension == INSIDE_CATEGORY:
            self._dimension = BY_CATEGORY
            self.dimension_control.set_data(BY_CATEGORY)
        self.dimension_control.set_enabled_values([TOTALS, BY_CATEGORY])
