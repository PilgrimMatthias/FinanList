from .models import ForecastMonth, ForecastInputs
from app.core.enums import OperationType
from datetime import datetime, date


def month_ordinal(year: int, month: int) -> int:
    """Months since year 0"""
    return year * 12 + (month - 1)


def occurrence_month(value) -> tuple[int, int]:
    """(year, month) of an occurrence, whether its date is a str or a date."""
    if isinstance(value, (datetime, date)):
        return value.year, value.month
    return int(value[0:4]), int(value[5:7])


def build_forecast(inputs: ForecastInputs) -> list[ForecastMonth]:
    """Metohod to forecast wallet amount month by month.

    Every month is the same arithmetic. The current month differs only in
    that its expenses already partly happened, so actuals are added in and
    the everyday estimate is reduced by what has already been spent.
    """
    months = []

    first = month_ordinal(inputs.today.year, inputs.today.month)
    last = first + inputs.horizon - 1

    # Bucket every occurrence by month in one pass rather than rescanning
    # the list for each month.
    buckets = {
        ordinal: {"expenses": 0.0, "savings": 0.0, "investments": 0.0}
        for ordinal in range(first, last + 1)
    }

    for item in inputs.scheduled:
        year, month = occurrence_month(item.date)
        ordinal = month_ordinal(year, month)

        # An overdue occurrence is dated in the past but is still yet to pay, so it belongs to the current month, not to a month already gone.
        if ordinal < first:
            ordinal = first
        if ordinal > last:
            continue

        bucket = buckets[ordinal]
        match item.operation_type:
            case OperationType.EXPENSE:
                bucket["expenses"] += item.amount
            case OperationType.SAVING:
                bucket["savings"] += item.amount
            case OperationType.INVESTMENT:
                bucket["investments"] += item.amount
            # INCOME occurrences are deliberately ignored - planned_income already covers the salary, and counting both double-counts it.

    planned_income = inputs.planned_income or 0.0
    planned_everyday = inputs.planned_everyday or 0.0

    opening = inputs.opening_balance

    for offset in range(inputs.horizon):
        ordinal = first + offset
        year, month = divmod(ordinal, 12)
        month += 1

        scheduled = buckets[ordinal]
        is_current = offset == 0

        if is_current:
            actuals = inputs.actuals_to_date

            # Income is the planned figure unless more has already arrived
            # than planned - a bonus, say. Never replace it with actuals
            # outright: a small refund early in the month would otherwise
            # become the whole month's income.
            income = max(planned_income, actuals.income)

            expenses = actuals.expenses + scheduled["expenses"]
            savings = actuals.savings + scheduled["savings"]
            investments = actuals.investments + scheduled["investments"]

            # Only the everyday part of actuals reduces the estimate.
            # Using actuals.expenses here would also subtract bills that
            # are already counted in the expenses column.
            est_other = max(0.0, planned_everyday - actuals.everyday)
            over_plan_by = (
                actuals.everyday - planned_everyday
                if actuals.everyday > planned_everyday
                else None
            )
        else:
            actuals = None
            income = planned_income
            expenses = scheduled["expenses"]
            savings = scheduled["savings"]
            investments = scheduled["investments"]
            # Future months have no cap to exceed - the plan is additive.
            est_other = planned_everyday
            over_plan_by = None

        closing = round(
            opening + income - expenses - savings - investments - est_other, 2
        )

        below_floor = inputs.floor is not None and closing < inputs.floor

        months.append(
            ForecastMonth(
                year=year,
                month=month,
                opening=opening,
                income=income,
                expenses=expenses,
                savings=savings,
                investments=investments,
                est_other=est_other,
                closing=closing,
                is_current_month=is_current,
                over_plan_by=over_plan_by,
                below_floor=below_floor,
                floor_gap=inputs.floor - closing if below_floor else None,
                actuals=actuals,
            )
        )

        opening = closing

    return months
