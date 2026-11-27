from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QColor, QCursor, QPen
from PySide6.QtWidgets import QToolTip

from app.core.utils import format_balance

from app.core.theme.palette import Palette
from app.core.widgets.themed_chart_view import ThemedChartView
from ..service import CategoryStats, MonthTotals
from .chart_helpers import hide_category_grid, month_label, value_axis_for

IN_PROGRESS_ALPHA = 110
IN_PROGRESS_MARK = "*"
CATEGORY_Y_TICKS = 5

# ThemedChartView zeroes the chart margins, which clips the topmost axis
# label in half. These charts put their own back.
CHART_MARGINS = QMargins(0, 10, 0, 0)


class TotalsChart(ThemedChartView):
    """Income beside expense, one pair per month.

    Grouped, not stacked. Income and expense are not parts of a whole, and
    stacking them would read as a total that means nothing.

    Month labels stay short and level - the year is in the table and the
    range pickers - and the month still being filled is marked "lis*".
    The legend is a ChartLegend above the chart, not the QtCharts one.
    """

    def __init__(self, parent=None, height: int = 220):
        super().__init__(parent=parent, height=height)
        self._rows: list[MonthTotals] = []
        self._current = None
        self._income_set = None
        self._expense_set = None
        self.restyled.connect(self._recolour)

    def set_rows(self, rows: list[MonthTotals], current=None):
        """`current` is (year, month) of the month still being filled."""
        self._rows = rows
        self._current = current

        if not rows:
            self.setChart(QChart())
            return

        self.set_chart(self._build())
        self.chart().setMargins(CHART_MARGINS)

    def _build(self) -> QChart:
        rows = self._rows

        self._income_set = QBarSet("Income")
        self._income_set.append([r.income for r in rows])
        self._expense_set = QBarSet("Expense")
        self._expense_set.append([r.expenses for r in rows])

        for bar_set in (self._income_set, self._expense_set):
            bar_set.setBorderColor(Qt.GlobalColor.transparent)

        series = QBarSeries()
        series.append(self._income_set)
        series.append(self._expense_set)
        series.setBarWidth(0.8)

        chart = QChart()
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        in_progress = self._in_progress_index()
        axis_x.append(
            [
                month_label(r.year, r.month)
                + (IN_PROGRESS_MARK if index == in_progress else "")
                for index, r in enumerate(rows)
            ]
        )
        # Past a year the short labels collide; only then tilt them.
        if len(rows) > 12:
            axis_x.setLabelsAngle(-45)

        axis_y = value_axis_for([r.income for r in rows], [r.expenses for r in rows])
        hide_category_grid(axis_x)

        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        series.hovered.connect(self._on_hover)

        self._recolour()
        return chart

    def has_in_progress(self) -> bool:
        """Whether the "* month in progress" note applies to this range."""
        return self._in_progress_index() is not None

    def _on_hover(self, status: bool, index: int, bar_set):
        """Exact figures on hover - the axis only gives the shape."""
        if not status or not (0 <= index < len(self._rows)):
            QToolTip.hideText()
            return

        row = self._rows[index]
        QToolTip.showText(
            QCursor.pos(),
            f"{month_label(row.year, row.month, True)}\n"
            f"Income {format_balance(row.income)}\n"
            f"Expense {format_balance(row.expenses)}\n"
            f"Difference {format_balance(row.difference)}",
        )

    def _recolour(self):
        if self._income_set is None:
            return

        self._income_set.setColor(QColor(Palette.color("chart_income")))
        self._expense_set.setColor(QColor(Palette.color("chart_expense")))

        # Dim the month that is not finished yet, so nobody reads a
        # half-filled column as a good month.
        index = self._in_progress_index()
        if index is None:
            return

        for bar_set in (self._income_set, self._expense_set):
            faded = QColor(bar_set.color())
            faded.setAlpha(IN_PROGRESS_ALPHA)
            bar_set.setSelectedColor(faded)
            bar_set.selectBar(index)

    def _in_progress_index(self) -> int | None:
        if self._current is None:
            return None
        for index, row in enumerate(self._rows):
            if (row.year, row.month) == self._current:
                return index
        return None


class CategoryChart(ThemedChartView):
    """One category month by month, with its average as a dashed line.

    Values sit on the bars rather than on a Y axis: there are at most
    twelve of them and the exact figure is the point, so an axis the
    reader has to interpolate against earns nothing.
    """

    def __init__(self, parent=None, height: int = 200):
        super().__init__(parent=parent, height=height)
        self._stats: CategoryStats = None
        self._months = []
        self._bar_set = None
        self._average = None
        self.restyled.connect(self._recolour)

    def set_stats(self, stats: CategoryStats, months: list[tuple[int, int]]):
        """`months` is the (year, month) list the values line up with."""
        self._stats = stats
        self._months = months

        if stats is None or not stats.monthly:
            self.setChart(QChart())
            return

        self.set_chart(self._build())
        self.chart().setMargins(CHART_MARGINS)

    def _build(self) -> QChart:
        values = self._stats.monthly

        self._bar_set = QBarSet(self._stats.name)
        self._bar_set.append(values)
        self._bar_set.setBorderColor(Qt.GlobalColor.transparent)

        series = QBarSeries()
        series.append(self._bar_set)
        series.setBarWidth(0.75)

        chart = QChart()
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        spans_years = len({y for y, _ in self._months}) > 1
        axis_x.append([month_label(y, m, spans_years) for y, m in self._months])
        if len(values) > 8:
            axis_x.setLabelsAngle(-45)

        axis_y = value_axis_for(values, ticks=CATEGORY_Y_TICKS)

        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        # The average needs a numeric X to span the full width; the
        # category axis would stop it at the first and last label.
        self._average = QLineSeries()
        self._average.setName("average")
        self._average.append(-0.5, self._stats.monthly_avg)
        self._average.append(len(values) - 0.5, self._stats.monthly_avg)

        axis_line_x = QValueAxis()
        axis_line_x.setRange(-0.5, len(values) - 0.5)
        axis_line_x.setVisible(False)

        chart.addSeries(self._average)
        chart.addAxis(axis_line_x, Qt.AlignmentFlag.AlignBottom)
        self._average.attachAxis(axis_line_x)
        self._average.attachAxis(axis_y)

        chart.legend().setVisible(False)
        series.hovered.connect(self._on_hover)

        self._recolour()
        return chart

    def _on_hover(self, status: bool, index: int, bar_set):
        if not status or not (0 <= index < len(self._months)):
            QToolTip.hideText()
            return

        year, month = self._months[index]
        QToolTip.showText(
            QCursor.pos(),
            f"{month_label(year, month, True)}\n"
            f"{format_balance(self._stats.monthly[index])}",
        )

    def _recolour(self):
        if self._bar_set is None:
            return

        self._bar_set.setColor(
            QColor(self._stats.color or Palette.color("category_fallback").name())
        )

        if self._average is not None:
            pen = QPen(Palette.color("text_secondary"))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)
            self._average.setPen(pen)
