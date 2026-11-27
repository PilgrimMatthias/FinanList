from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QLineSeries,
    QStackedBarSeries,
    QValueAxis,
    QXYSeries,
)
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QColor, QPen, QFont

from app.core.theme.palette import Palette
from app.core.widgets.themed_chart_view import ThemedChartView
from ..forecast.forecast import ForecastMonth
from .chart_helpers import grouped, hide_category_grid, month_label, value_axis_for

SERIES = (
    ("Expenses", "chart_expense", lambda r: r.expenses),
    ("Savings", "chart_saving", lambda r: r.savings),
    ("Investments", "chart_investment", lambda r: r.investments),
    ("Est. other", "chart_estimate", lambda r: r.est_other),
)
ESTIMATE = "Est. other"

POINT_SIZE = 7
POINT_RADIUS = 4.0
LABEL_SIZE_BUMP = 2.0
MAX_UNROTATED_LABELS = 6

CHART_MARGINS = QMargins(0, 22, 0, 0)

PointConfig = QXYSeries.PointConfiguration


class ForecastChart(ThemedChartView):
    """Stacked outflow bars with the projected balance and the floor over them."""

    def __init__(self, parent=None, height: int = 260):
        super().__init__(parent=parent, height=height)
        self._rows: list[ForecastMonth] = []
        self._floor = None
        self._bar_sets = {}
        self._balance = None
        self._floor_line = None
        # Re-colour on theme change; the base class repaints the chrome.
        self.restyled.connect(self._recolour)

    def set_rows(self, rows: list[ForecastMonth], floor: float = None):
        self._rows = rows
        self._floor = floor

        if not rows:
            self.setChart(QChart())
            return

        self.set_chart(self._build())
        self.chart().setMargins(CHART_MARGINS)

    def _build(self) -> QChart:
        rows = self._rows

        bars = QStackedBarSeries()
        bars.setBarWidth(0.5)
        self._bar_sets = {}

        for label, _key, pick in SERIES:
            bar_set = QBarSet(label)
            bar_set.append([pick(r) for r in rows])
            bars.append(bar_set)
            self._bar_sets[label] = bar_set

        self._balance = QLineSeries()
        self._balance.setName("Balance")
        for i, row in enumerate(rows):
            self._balance.append(i, row.closing)

        chart = QChart()
        chart.addSeries(bars)

        axis_x = QBarCategoryAxis()
        axis_x.append([month_label(r.year, r.month, with_year=True) for r in rows])
        # Twelve "lis 26" labels will not fit side by side at 800px.
        if len(rows) > MAX_UNROTATED_LABELS:
            axis_x.setLabelsAngle(-45)

        stacked_totals = [
            r.expenses + r.savings + r.investments + r.est_other for r in rows
        ]
        balances = [r.closing for r in rows]
        floor_values = [self._floor] if self._floor is not None else []

        # Derived, never a constant - a hardcoded maximum clips the first month that exceeds it, silently.
        axis_y = value_axis_for(stacked_totals, balances, floor_values)
        hide_category_grid(axis_x)

        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bars.attachAxis(axis_x)
        bars.attachAxis(axis_y)

        axis_line_x = QValueAxis()
        axis_line_x.setRange(-0.5, len(rows) - 0.5)
        axis_line_x.setVisible(False)
        chart.addAxis(axis_line_x, Qt.AlignmentFlag.AlignBottom)

        self._floor_line = None
        if self._floor is not None:
            self._floor_line = QLineSeries()
            self._floor_line.setName("Floor")
            self._floor_line.append(-0.5, self._floor)
            self._floor_line.append(len(rows) - 0.5, self._floor)
            chart.addSeries(self._floor_line)
            self._floor_line.attachAxis(axis_line_x)
            self._floor_line.attachAxis(axis_y)

        # Added last so the balance and its labels draw over the floor.
        chart.addSeries(self._balance)
        self._balance.attachAxis(axis_line_x)
        self._balance.attachAxis(axis_y)

        chart.legend().setVisible(False)

        self._recolour()
        return chart

    def _recolour(self):
        """Series colours are data, so they are re-applied on theme change."""
        for label, key, _pick in SERIES:
            bar_set = self._bar_sets.get(label)
            if bar_set is None:
                continue
            bar_set.setColor(QColor(Palette.color(key)))

            if label == ESTIMATE:
                border = QPen(Palette.color("chart_estimate_border"))
                border.setStyle(Qt.PenStyle.DashLine)
                border.setWidth(1)
                bar_set.setPen(border)
            else:
                bar_set.setBorderColor(Qt.GlobalColor.transparent)

        if self._floor_line is not None:
            pen = QPen(Palette.color("chart_floor"))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)
            self._floor_line.setPen(pen)

        if self._balance is not None:
            self._style_balance()

    @staticmethod
    def _label_point_size(font: QFont) -> float:
        """Balance label size: one step under the body text, plus 2pt."""
        base = font.pointSizeF()
        if base <= 0 and font.pixelSize() > 0:
            base = font.pixelSize() * 0.75
        if base <= 0:
            base = 9.0
        return max(7.0, base - 1) + LABEL_SIZE_BUMP

    def _style_balance(self):
        """Line, hollow points and a value label over each point."""
        line_colour = Palette.color("chart_balance")

        pen = QPen(line_colour)
        pen.setWidth(2)
        self._balance.setPen(pen)
        self._balance.setPointsVisible(True)
        self._balance.setMarkerSize(POINT_SIZE)
        self._balance.setBrush(Palette.color("surface"))

        self._balance.setPointLabelsVisible(True)
        self._balance.setPointLabelsColor(line_colour)
        self._balance.setPointLabelsClipping(False)
        label_font = QFont(self.font())
        label_font.setPointSizeF(self._label_point_size(label_font))
        label_font.setWeight(QFont.Weight.DemiBold)
        self._balance.setPointLabelsFont(label_font)

        floor_colour = Palette.color("chart_floor")

        for index, row in enumerate(self._rows):
            config = {
                PointConfig.LabelVisibility: True,
                PointConfig.LabelFormat: grouped(row.closing),
                # Without an explicit size a configured point is drawn at
                # double the marker size and its label lands on top of it.
                PointConfig.Size: POINT_RADIUS,
                PointConfig.Color: floor_colour if row.below_floor else line_colour,
            }
            self._balance.setPointConfiguration(index, config)
