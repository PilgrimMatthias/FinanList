from app.core import AppState
from app.database.repositories import (
    WalletRepo,
    RecurringTransactionRepo,
    TransactionRepo,
    UserRepo
)
from app.features.upcoming.service import UpcomingService
from app.database.models import Wallet, Transaction, RecurringTransaction
from app.core.enums import Currency
from .models import MonthSummary, CategoryTotal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.core.utils import cast_datetime_to_str, cast_str_to_datetime
from app.features.history.models import TransactionDisplay
from app.features.upcoming.models import RecurringTransactionDisplay
from babel.dates import get_month_names
from datetime import date
import locale

class DashboardService:
    def __init__(
        self,
        wallet_repo: WalletRepo,
        recurring_transaction_repo: RecurringTransactionRepo,
        transaction_repo: TransactionRepo,
        user_repo: UserRepo,
        upcoming_service: UpcomingService,
        app_state: AppState,
    ):
        self.wallet_repo = wallet_repo
        self.recurring_transaction_repo = recurring_transaction_repo
        self.transaction_repo = transaction_repo
        self.upcoming_service = upcoming_service
        self.user_repo = user_repo
        self.app_state = app_state

    def get_current_month_name(self) -> str:
        """Return month name with proper formatting"""
        today = date.today()

        loc = locale.getlocale()[0] or "en_US"
        months = get_month_names(
            width="wide",
            context="stand-alone",
            locale=loc
        )

        return f"{months[today.month]}"


    def get_user_name(self, user_id:int) -> str:
        """Returns user name"""
        user = self.user_repo.get_user_by_id(id = user_id)

        return user.name

    def get_balance(self, wallet_id: int) -> float:
        """Returns balance for wallet"""
        return self.wallet_repo.get_balance(wallet_id=wallet_id)

    def get_wallet(self, wallet_id: int) -> Wallet:
        """Returns wallet by wallet id"""
        return self.wallet_repo.get_by_id(id = wallet_id)

    def get_month_summary(self, wallet_id: int, year:int, month:int) -> MonthSummary:
        """Returns cashflow summary for month, year and choosen wallet"""
        date_from = datetime(year=year, month=month, day=1)
        date_to = date_from + relativedelta(day=31)

        rows = self.transaction_repo.get_month_totals(
            wallet_id=wallet_id,
            date_from=cast_datetime_to_str(date_from, "%Y-%m-%d"),
            date_to=cast_datetime_to_str(date_to, "%Y-%m-%d")
        )

        income = sum([row[1] for row in rows if row[0] == "Income"])
        outgoing = sum([row[1] for row in rows if row[0] != "Income"])
        net = income - outgoing

        month_summary = MonthSummary(
            income=income,
            outgoing=outgoing,
            net=net,
            by_type={row[0]: row[1] for row in rows}
        )

        return month_summary

    def get_category_totals(self, wallet_id:int, year:int, month:int, top_n:int=3) -> list[CategoryTotal]:
        """Returns expenses by category"""
        date_from = datetime(year=year, month=month, day=1)
        date_to = date_from + relativedelta(day=31)

        rows = self.transaction_repo.get_category_totals(
            wallet_id=wallet_id,
            date_from=cast_datetime_to_str(date_from, "%Y-%m-%d"),
            date_to=cast_datetime_to_str(date_to, "%Y-%m-%d")
        )

        total = sum([row[3] for row in rows])

        top = rows[:top_n]
        rest = rows[top_n:]

        category_totals = [
            CategoryTotal(row[0], row[1], row[2], row[3], self._calculate_share(row[3], total))
            for row in top
        ]

        if rest:
            rest_sum = sum(r[3] for r in rest)
            category_totals.append(CategoryTotal(
                category_id=-1,
                name=f"Other ({len(rest)})",
                color="#808080",
                amount=rest_sum,
                total_percentage=self._calculate_share(rest_sum, total),
            ))

        return category_totals

    def get_recent(self, wallet_id:int, limit:int=5) -> list[TransactionDisplay]:
        """Return recent transactions"""
        rows = self.transaction_repo.get_paginated(
            wallet_id=wallet_id,
            page = 1,
            page_size = limit,
            sort_by = "date",
            sort_order = "DESC",
        )

        return [self._transaction_to_display(row) for row in rows]

    def get_upcomings(self, wallet_id:int, limit:int=5) -> list[RecurringTransactionDisplay]:
        """Returns list of upcoming transactions"""
        date_from = datetime.today()
        rows = self.recurring_transaction_repo.get_upcomings(
            wallet_id=wallet_id,
            date_from=cast_datetime_to_str(date_from, "%Y-%m-%d"),
            limit=limit
        )

        return [self._recurring_to_display(row) for row in rows]

    def get_due_count(self, wallet_id: int) -> int: 
        """Get due transaction count for display"""
        return self.upcoming_service.get_due_count(wallet_id=wallet_id)
    
    # Helpers
    def _calculate_share(self, amount:float, total:float) -> float:
        """Calculate percentage of total based for provided amount"""
        try:
            return amount / total
        except ZeroDivisionError:
            return 0.0

    def _transaction_to_display(self, row: tuple) -> TransactionDisplay:
        """Returns TransactionDisplay from specified row"""
        transaction = Transaction.from_row(row)

        transaction_display = TransactionDisplay(
            transaction=transaction,
            main_category_name=row[11] or "—",
            main_category_color=row[12] or "#808080",
            sub_category_name=row[13] or "—",
            sub_category_color=row[14] or "#808080",
            is_recurring=row[9] is not None,
        )

        return transaction_display

    def _recurring_to_display(self, row: tuple) -> RecurringTransactionDisplay:
        """Returns TransactionDisplay from specified row"""
        rec_transaction = RecurringTransaction.from_row(row)

        next_due_date = cast_str_to_datetime(row[11], format="%Y-%m-%d")

        transaction_display = RecurringTransactionDisplay(
            recurring=rec_transaction,
            main_category_name=row[14],
            main_category_color=row[15],
            sub_category_name=row[16],
            sub_category_color=row[17],
            days_until_due=(next_due_date - datetime.today()).days,
            currency=Currency(row[18])
        )

        return transaction_display


    def get_due_transactions(self, wallet_id: int, today: datetime | None = None) -> list[RecurringTransactionDisplay]: 
        """Get due transactions for display"""
        return self.upcoming_service.get_due_transactions(wallet_id=wallet_id, today=today)