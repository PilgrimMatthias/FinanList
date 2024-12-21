import numpy as np
import math
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QBarSet,
    QBarSeries,
    QValueAxis,
    QBarCategoryAxis,
    QScatterSeries,
)
from finance_app.config import COLORS


class BarChart(QWidget):
    """
    Bar chart widget to display user operations.
    """

    def __init__(
        self,
        parent,
        data,
        title="Bar chart",
        legend=False,
        x_label=None,
        x_axis_visible=True,
        y_label=None,
        y_axis_visible=True,
        colors=COLORS,
        gridlines=True,
        tootltip=None,
    ):
        super().__init__()
        self.data = data
        self.title = title
        self.legend = legend
        self.x_label = x_label
        self.x_axis_visible = x_axis_visible
        self.y_label = x_label
        self.y_axis_visible = y_axis_visible
        self.colors = colors
        self.gridlines = gridlines
        self.tooltip = tootltip

        self.marker_font = QFont()
        self.marker_font.setPointSize(11)

        self.init_chart()

    def init_chart(self):
        """
        Chart initialize
        """
        # Set up the chart
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setTitleFont(QFont("Arial", 14))
        self.chart.setContentsMargins(0, 0, 0, 0)
        self.chart.legend().hide()

        # Setting tooltip
        if self.tooltip is not None:
            self.chart.setToolTip(self.tooltip)

        # Min and max val for y axis
        min_val = self.data.unstack().min()
        max_val = self.data[self.data > 0].sum(axis=1).max()
        if len(self.data.columns) > 2:
            max_val = self.data.unstack().max()
        elif len(self.data.index) == 2:
            min_val *= min_val * 0.2
        elif len(self.data.index) == 1:
            max_val = int(math.ceil(self.data.unstack().max() / 1000)) * 1000
            max_val = max_val + max_val * 0.2
            min_val = 0

        # Y-axis
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText("[złoty]")
        self.y_axis.setTitleFont(QFont("Arial", 11))
        self.y_axis.setLabelFormat("%.0f")
        self.y_axis.setRange(min_val, max_val)
        self.y_axis.applyNiceNumbers()
        self.y_axis.setGridLineVisible(self.gridlines)

        if self.y_label is not None:
            self.y_axis.setTitleText(self.y_label)
            self.y_axis.setTitleFont(QFont("Arial", 11))

        # X-axis
        self.x_axis = QBarCategoryAxis()
        self.x_axis.append(self.data.index)
        self.x_axis.setGridLineVisible(self.gridlines)

        if self.x_label is not None:
            self.x_axis.setTitleText(self.x_label)
            self.x_axis.setTitleFont(QFont("Arial", 11))
            self.x_axis.setTitleBrush(QBrush("#666666"))

        # Adding bars to series
        self.bar_series = QBarSeries()
        self.bar_series.setBarWidth(0.7)

        for col in self.data.columns:
            bar_set = QBarSet(col)
            for value in self.data[col]:
                bar_set.append(value - 250)
                bar_set.setColor(self.colors.get(col))

            self.bar_series.append(bar_set)

        # Add the series to the chart
        self.chart.addSeries(self.bar_series)

        # Scatter series for displaying values in text above bars
        self.marker_series = QScatterSeries()

        # Setting scatter series
        self.marker_series.setMarkerSize(7)
        self.marker_series.setColor(QColor("white"))
        self.marker_series.setBorderColor(QColor("white"))
        self.marker_series.setPointLabelsFormat("@yPoint")
        self.marker_series.setPointLabelsVisible(True)
        self.marker_series.setPointLabelsFont(self.marker_font)
        self.marker_series.setPointLabelsColor("#4d4d4d")
        self.marker_series.setPointLabelsClipping(False)

        # Adding values above bars
        for col_num, col in enumerate(self.data.columns):
            index = 0
            differ_vals = np.linspace(0, 1, num=len(self.data.columns) + 5)[
                1:-1
            ]  # List of values
            differ_vals = [differ_vals[0]] * len(
                self.data.columns
            )  # Creating list of x positions at the center of bar
            differ_vals = [
                -val if i % 2 == 0 else val for i, val in enumerate(differ_vals)
            ]
            differ = 0

            # Adding markers
            for value in self.data[col]:
                if len(self.data.columns) > 1:
                    differ = differ_vals[col_num]
                self.marker_series.append(index + differ, round(value, 0))
                index += 1

        self.chart.addSeries(self.marker_series)

        # Setting axis
        self.chart.setAxisX(self.x_axis)
        self.chart.setAxisY(self.y_axis)

        self.bar_series.attachAxis(self.y_axis)
        self.bar_series.attachAxis(self.x_axis)

        self.marker_series.attachAxis(self.x_axis)
        self.marker_series.attachAxis(self.y_axis)

        self.chart.axisY().setVisible(self.y_axis_visible)
        self.chart.axisX().setVisible(self.x_axis_visible)

        # Set up the legend
        if self.legend:
            self.chart.legend().show()
            self.chart.legend().setFont(QFont("Arial", 12))
            for index, marker in enumerate(self.chart.legend().markers()):
                if index >= len(self.data.columns):
                    marker.setVisible(False)  # Hide scatter series from legend

        # Set up the chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(self.chart_view.renderHints())

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
