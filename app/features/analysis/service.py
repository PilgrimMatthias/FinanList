from dataclasses import dataclass, replace
from datetime import date, datetime, time

from app.core import AppState
from app.core.exceptions import ValidationError
from app.core.enums import OperationType, RecurrenceInterval
from dateutil.relativedelta import relativedelta
from app.core.utils import shift_month, cast_str_to_datetime
from app.database.models import Transaction
from app.database.repositories import (
    WalletRepo,
    TransactionRepo,
    RecurringTransactionRepo,
)
from .forecast.forecast import (
    ForecastInputs,
    ForecastMonth,
    build_forecast,
)
from .forecast.models import MonthActuals

MAX_OCCURRENCES_PER_RECURRING = 500

OUTFLOW_TYPES = (OperationType.EXPENSE, OperationType.SAVING, OperationType.INVESTMENT)


@dataclass(frozen=True)
class CategoryStats:
    """One row of the Trends by-category table."""

    category_id: int
    name: str
    color: str
    total: float
    monthly_avg: float
    minimum: float
    maximum: float
    share: float  # fraction of the whole, 0.0 - 1.0
    monthly: list[float]  # one value per month, zero-filled


@dataclass(frozen=True)
class Assumptions:
    """What the projection was built from, as the strip displays it."""

    planned_income: float | None
    planned_everyday: float | None
    floor: float | None

    @property
    def is_complete(self) -> bool:
        """A forecast without these two is a straight line at zero."""
        return self.planned_income is not None and self.planned_everyday is not None


@dataclass(frozen=True)
class MonthTotals:
    """One row of the Trends totals table."""

    year: int
    month: int
    income: float
    expenses: float
    savings: float
    investments: float

    @property
    def difference(self) -> float:
        return self.income - self.expenses - self.savings - self.investments

    @property
    def savings_rate(self) -> float | None:
        return self.difference / self.income if self.income else None


def month_key(year: int, month: int) -> str:
    """'YYYY-MM', matching strftime in the repo queries."""
    return f"{year:04d}-{month:02d}"


def month_range(start: date, count: int) -> list[tuple[int, int]]:
    """count months as (year, month), starting at start's month."""
    return [shift_month(start.year, start.month, offset) for offset in range(count)]


def month_bounds(year: int, month: int, count: int) -> tuple[date, date]:
    """[from, to) spanning count months from (year, month). to is EXCLUSIVE."""
    end_year, end_month = shift_month(year, month, count)
    return date(year, month, 1), date(end_year, end_month, 1)


class AnalysisService:
    """Forecast and Trends, scoped to one wallet."""

    def __init__(
        self,
        wallet_repo: WalletRepo,
        transaction_repo: TransactionRepo,
        recurring_transaction_repo: RecurringTransactionRepo,
        app_state: AppState,
    ):
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo
        self.recurring_transaction_repo = recurring_transaction_repo
        self.app_state = app_state

    # Forecast
    def get_forecast(
        self, wallet_id: int, horizon: int, today: date = None
    ) -> list[ForecastMonth]:
        """Gather everything build_forecast needs, then compute."""
        today = today or date.today()
        wallet = self.wallet_repo.get_by_id(id=wallet_id)

        month_start, horizon_end = month_bounds(today.year, today.month, horizon)

        inputs = ForecastInputs(
            opening_balance=self.wallet_repo.get_balance_at(
                wallet_id=wallet_id, as_of=month_start.isoformat()
            ),
            planned_income=wallet.net_salary_monthly,
            planned_everyday=wallet.everyday_spending_monthly,
            floor=wallet.forecast_floor,
            scheduled=self.get_scheduled_occurrences(
                wallet_id=wallet_id,
                end=datetime.combine(horizon_end, time.min),
            ),
            horizon=horizon,
            today=today,
            actuals_to_date=self.get_month_actuals(wallet_id=wallet_id, today=today),
        )
        return build_forecast(inputs)

    def get_month_actuals(self, wallet_id: int, today: date = None) -> MonthActuals:
        """Current month to date, with the everyday split the clamp needs."""
        today = today or date.today()
        month_start, next_month = month_bounds(today.year, today.month, 1)

        rows = self.transaction_repo.get_month_actuals(
            wallet_id=wallet_id,
            date_from=month_start.isoformat(),
            date_to=next_month.isoformat(),
        )

        totals = {op: 0.0 for op in OperationType}
        everyday = 0.0

        for operation_type, is_recurring, total in rows:
            op = OperationType(operation_type)
            totals[op] += total or 0.0
            if op is OperationType.EXPENSE and not is_recurring:
                everyday += total or 0.0

        return MonthActuals(
            income=totals[OperationType.INCOME],
            expenses=totals[OperationType.EXPENSE],
            everyday=everyday,
            savings=totals[OperationType.SAVING],
            investments=totals[OperationType.INVESTMENT],
        )

    def get_scheduled_occurrences(
        self, wallet_id: int, end: datetime = None
    ) -> list[Transaction]:
        """Unconfirmed occurrences before `end`, as unsaved Transactions.

        Read-only. Generation never writes - the due dialog's confirmation
        path does that.

        Generation starts at next_due_date, which may already be in the past
        for an overdue item. That is deliberate: an overdue bill is still
        yet to pay, and build_forecast buckets anything before the horizon
        into the current month.
        """
        end = end or datetime.today()

        recurrings = self.recurring_transaction_repo.get_active_by_wallet_id(
            wallet_id=wallet_id,
        )

        occurrences = []

        for recurring in recurrings:
            existing_dates = {
                cast_str_to_datetime(d)
                for d in self.transaction_repo.get_dates_for_recurring(recurring.id)
            }

            occurrence_date = cast_str_to_datetime(recurring.next_due_date)

            recurrence_end = getattr(recurring, "end_date", None)
            if recurrence_end:
                recurrence_end = cast_str_to_datetime(recurrence_end)

            generated = 0

            # The condition must advance. Testing a fixed start <= end never
            # changes and runs until memory gives out.
            while occurrence_date < end:
                if generated >= MAX_OCCURRENCES_PER_RECURRING:
                    break
                if recurrence_end and occurrence_date > recurrence_end:
                    break

                if occurrence_date not in existing_dates:
                    occurrences.append(
                        Transaction(
                            wallet_id=recurring.wallet_id,
                            category_id=recurring.category_id,
                            title=recurring.title,
                            description=recurring.description,
                            date=occurrence_date,
                            operation_type=recurring.operation_type,
                            amount=recurring.amount,
                            merchant=recurring.merchant,
                            recurring_id=recurring.id,
                        )
                    )

                next_date = self._calculate_next_date(
                    occurrence_date, recurring.recurrence_interval
                )

                # An interval that fails to move the date would loop forever.
                if next_date <= occurrence_date:
                    break

                occurrence_date = next_date
                generated += 1

        return occurrences

    # Trends
    def get_totals(self, wallet_id: int, start: date, months: int) -> list[MonthTotals]:
        """Income / expenses / savings / investments per month."""
        date_from, date_to = month_bounds(start.year, start.month, months)

        rows = self.transaction_repo.get_monthly_totals(
            wallet_id=wallet_id,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
        )

        buckets = {}
        for year_month, operation_type, total in rows:
            buckets.setdefault(year_month, {})[OperationType(operation_type)] = (
                total or 0.0
            )

        out = []
        for year, month in month_range(start, months):
            found = buckets.get(month_key(year, month), {})
            out.append(
                MonthTotals(
                    year=year,
                    month=month,
                    income=found.get(OperationType.INCOME, 0.0),
                    expenses=found.get(OperationType.EXPENSE, 0.0),
                    savings=found.get(OperationType.SAVING, 0.0),
                    investments=found.get(OperationType.INVESTMENT, 0.0),
                )
            )
        return out

    def get_by_category(
        self,
        wallet_id: int,
        start: date,
        months: int,
        operation_types: tuple[OperationType, ...] = OUTFLOW_TYPES,
    ) -> list[CategoryStats]:
        """Main-category breakdown over the range, all outflows by default."""
        date_from, date_to = month_bounds(start.year, start.month, months)

        rows = self.transaction_repo.get_category_monthly_totals(
            wallet_id=wallet_id,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            operation_types=[t.value for t in operation_types],
        )
        return self._to_stats(rows, start, months)

    def get_inside_category(
        self,
        wallet_id: int,
        parent_id: int,
        start: date,
        months: int,
        operation_types: tuple[OperationType, ...] = OUTFLOW_TYPES,
    ) -> list[CategoryStats]:
        """Subcategory breakdown inside one main category."""
        date_from, date_to = month_bounds(start.year, start.month, months)

        rows = self.transaction_repo.get_subcategory_monthly_totals(
            wallet_id=wallet_id,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            operation_types=[t.value for t in operation_types],
            parent_id=parent_id,
        )
        return self._to_stats(rows, start, months)

    @staticmethod
    def _to_stats(rows: list[tuple], start: date, months: int) -> list[CategoryStats]:
        """Turn a raw month x category grid into one row per category.

        Zero-fills months a category is absent from. SQL's AVG and MIN only
        see rows that exist, so a category spent in 3 of 6 months would
        report twice its real average and never report a minimum of zero.
        """
        keys = [month_key(y, m) for y, m in month_range(start, months)]

        meta = {}
        grid = {}
        for year_month, cat_id, name, color, total in rows:
            meta[cat_id] = (name, color)
            grid.setdefault(cat_id, {})[year_month] = total or 0.0

        stats = []
        for cat_id, (name, color) in meta.items():
            monthly = [grid[cat_id].get(key, 0.0) for key in keys]
            total = sum(monthly)
            stats.append(
                CategoryStats(
                    category_id=cat_id,
                    name=name,
                    color=color,
                    total=total,
                    monthly_avg=total / months if months else 0.0,
                    minimum=min(monthly),
                    maximum=max(monthly),
                    share=0.0,
                    monthly=monthly,
                )
            )

        grand_total = sum(s.total for s in stats)
        if grand_total:
            stats = [replace(s, share=s.total / grand_total) for s in stats]

        return sorted(stats, key=lambda s: s.total, reverse=True)

    def get_assumptions(self, wallet_id: int) -> Assumptions:
        wallet = self.wallet_repo.get_by_id(id=wallet_id)
        return Assumptions(
            planned_income=wallet.net_salary_monthly,
            planned_everyday=wallet.everyday_spending_monthly,
            floor=wallet.forecast_floor,
        )

    def _calculate_next_date(self, current_date, interval):
        """Calculate next date with specified interval"""
        match interval:
            case RecurrenceInterval.DAILY:
                return current_date + relativedelta(days=1)
            case RecurrenceInterval.WEEKLY:
                return current_date + relativedelta(weeks=1)
            case RecurrenceInterval.MONTHLY:
                return current_date + relativedelta(months=1)
            case RecurrenceInterval.YEARLY:
                return current_date + relativedelta(years=1)
            case _:
                raise ValidationError(f"Unsupported recurrence interval: {interval}")
