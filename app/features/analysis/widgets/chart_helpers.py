from math import ceil

from PySide6.QtCharts import QCategoryAxis

from app.core.widgets.themed_chart_view import ThemedChartView, AXIS_HEADROOM

MONTHS_SHORT = (
    "sty",
    "lut",
    "mar",
    "kwi",
    "maj",
    "cze",
    "lip",
    "sie",
    "wrz",
    "paź",
    "lis",
    "gru",
)

MONTHS_FULL = (
    "Styczeń",
    "Luty",
    "Marzec",
    "Kwiecień",
    "Maj",
    "Czerwiec",
    "Lipiec",
    "Sierpień",
    "Wrzesień",
    "Październik",
    "Listopad",
    "Grudzień",
)

Y_TICKS = 3


def grouped(value: float) -> str:
    """12345.6 -> '12 346'. Axis and point labels drop the grosze."""
    return f"{round(value):,}".replace(",", " ")


def value_axis(maximum: float, ticks: int = Y_TICKS) -> QCategoryAxis:
    """A Y axis whose labels match the rest of the app."""
    # Round the step, not just the top, so every gridline lands on a number someone would say out loud: 0 / 4 000 / 8 000 / 12 000.
    step = ThemedChartView.nice_ceiling(maximum / ticks, headroom=1.0)
    top = step * max(1, ceil(maximum / step - 1e-9))

    axis = QCategoryAxis()
    axis.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
    axis.setRange(0, top)
    axis.setStartValue(0)

    # A tiny range (every month zero) would round several ticks to the
    # same label and stack them on top of each other.
    seen = set()
    value = 0.0
    while value <= top + 1e-9:
        label = grouped(value)
        if label not in seen:
            seen.add(label)
            axis.append(label, value)
        value += step

    return axis


def value_axis_for(*value_groups, ticks: int = Y_TICKS) -> QCategoryAxis:
    """value_axis over every series that shares it, with headroom."""
    values = [v for group in value_groups for v in group if v is not None]
    maximum = max(values, default=0) * AXIS_HEADROOM
    return value_axis(maximum if maximum > 0 else 1.0, ticks=ticks)


def hide_category_grid(axis):
    """Bars already mark each month; vertical gridlines only add noise."""
    axis.setGridLineVisible(False)
    axis.setMinorGridLineVisible(False)


def month_label(year: int, month: int, with_year=False) -> str:
    """'lis' or 'lis 26'."""
    if with_year:
        return f"{MONTHS_SHORT[month - 1]} {str(year)[2:]}"
    return MONTHS_SHORT[month - 1]


def month_full(year: int, month: int) -> str:
    """'Listopad 2026'."""
    return f"{MONTHS_FULL[month - 1]} {year}"
