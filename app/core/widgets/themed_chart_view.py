from math import floor, log10

from PySide6.QtCharts import QChart, QChartView
from PySide6.QtCore import Qt, Signal, QMargins, QEvent
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QAbstractScrollArea, QApplication

from app.core.theme.palette import Palette, palette_signals

# Multipliers used to round an axis maximum up to a readable number.
NICE_STEPS = (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10)
AXIS_HEADROOM = 1.08


class ThemedChartView(QChartView):
    """QChartView that follows the app theme.

    The view styles only: axis labels, grid lines, axis lines and the legendd.
    """

    restyled = Signal()

    def __init__(self, parent=None, chart=None, height: int = None):
        """
        Args:
            chart (QChart, optional): chart to display. Defaults to None.
            height (int, optional): fixed height in px. Defaults to None.
        """
        super().__init__(parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QChartView.Shape.NoFrame)
        self.setBackgroundBrush(Qt.BrushStyle.NoBrush)

        if height is not None:
            self.setFixedHeight(height)

        # The wheel arrives at the viewport, not at this widget.
        self.viewport().installEventFilter(self)

        palette_signals.changed.connect(self.restyle)

        if chart is not None:
            self.set_chart(chart)

    def set_chart(self, chart: QChart):
        """Display a chart and theme it."""
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        chart.setBackgroundRoundness(0)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)

        self.setChart(chart)
        self.restyle()

    def restyle(self, theme: str = None):
        """Re-read the palette and repaint the chrome.

        Connected to palette_signals.changed, which passes the theme name -
        it is ignored because Palette has already switched by then.
        """
        chart = self.chart()
        if chart is None:
            return

        label_color = Palette.color("text_secondary")
        grid_color = Palette.color("separator")
        line_color = Palette.color("border")

        for axis in chart.axes():
            axis.setLabelsColor(label_color)
            axis.setTitleBrush(label_color)
            axis.setGridLineColor(grid_color)
            axis.setLinePenColor(line_color)
            axis.setMinorGridLineColor(grid_color)
            axis.setShadesVisible(False)

        legend = chart.legend()
        legend.setLabelColor(label_color)
        legend.setBackgroundVisible(False)
        legend.setBorderColor(Qt.GlobalColor.transparent)

        self.restyled.emit()

    def eventFilter(self, watched, event):
        """Hand the wheel to the nearest scrollable ancestor."""
        if watched is self.viewport() and event.type() == QEvent.Type.Wheel:
            target = self.parent()
            while target is not None:
                if isinstance(target, QAbstractScrollArea):
                    QApplication.sendEvent(target.viewport(), event)
                    return True
                target = target.parent()
            # No scrollable ancestor - swallow it rather than let the
            # graphics view pan the scene.
            return True

        return super().eventFilter(watched, event)

    def wheelEvent(self, event):
        """Belt and braces for a wheel delivered straight to the widget."""
        event.ignore()

    @staticmethod
    def nice_ceiling(value: float, headroom: float = AXIS_HEADROOM) -> float:
        """Round a maximum up to a readable axis bound.

        Args:
            value (float): largest value the axis must show.
            headroom (float): space left above it. Defaults to 1.08.
        """
        if value is None or value <= 0:
            return 1.0

        target = value * headroom
        magnitude = 10 ** floor(log10(target))

        for step in NICE_STEPS:
            candidate = step * magnitude
            if candidate >= target:
                return float(candidate)

        return float(10 * magnitude)

    @classmethod
    def axis_maximum(cls, *value_groups, headroom: float = AXIS_HEADROOM) -> float:
        """nice_ceiling over several series at once.
        axis_maximum(stacked_totals, balances, [floor])
        """
        values = [v for group in value_groups for v in group if v is not None]
        return cls.nice_ceiling(max(values, default=0), headroom)
