from dataclasses import dataclass
from app.database.models import Transaction
from datetime import date


@dataclass(frozen=True)
class MonthActuals:
    income: float = 0.0
    expenses: float = 0.0
    everyday: float = 0.0  # the recurring_id IS NULL subset of them
    savings: float = 0.0
    investments: float = 0.0


@dataclass
class ForecastMonth:
    year: int
    month: int
    opening: float
    income: float
    expenses: float
    savings: float
    investments: float
    est_other: float
    closing: float
    is_current_month: bool
    over_plan_by: float | None = None
    below_floor: bool = False
    floor_gap: float | None = None
    actuals: MonthActuals | None = None


@dataclass(frozen=True)
class ForecastInputs:
    opening_balance: float
    planned_income: float | None
    planned_everyday: float
    floor: float | None
    scheduled: list[Transaction]
    actuals_to_date: MonthActuals
    horizon: int
    today: date
