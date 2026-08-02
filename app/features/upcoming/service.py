from app.core import AppState
from app.database.repositories import (
    RecurringTransactionRepo,
    TransactionRepo
)
from .models import RecurringTransactionDisplay
from app.database.models import RecurringTransaction, Transaction
from app.core.utils import cast_str_to_datetime, cast_datetime_to_str
from datetime import datetime
from app.core.enums import Currency, RecurrenceInterval
from dateutil.relativedelta import relativedelta
from app.core.exceptions import ValidationError

class UpcomingService:
    def __init__(
        self,
        recurring_transaction_repo: RecurringTransactionRepo,
        transaction_repo: TransactionRepo,
        app_state: AppState,
    ):
        self.recurring_transaction_repo = recurring_transaction_repo
        self.transaction_repo = transaction_repo
        self.app_state = app_state

    # Get methods
    def get_paginated_for_display(
        self,
        wallet_id: int,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
        search: str = "",
    ) -> list[RecurringTransactionDisplay]:
        """Get paginated transactions for display"""
        rows = self.recurring_transaction_repo.get_paginated(
            wallet_id=wallet_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search
        )
        return [self._row_to_display(row) for row in rows]
    
    def get_count(self, wallet_id:int, search: str = "") -> int:
        """Get count of recurring transactions"""
        return self.recurring_transaction_repo.get_count(wallet_id=wallet_id, search=search)


    def get_due_transactions(self, wallet_id: int, today: datetime | None = None) -> list[RecurringTransactionDisplay]: 
        """Get due transactions for display"""
        # Get due recurrings
        today = today or datetime.today()
        rows = self.recurring_transaction_repo.get_due(
            wallet_id=wallet_id,
            today=today
        )

        due_transactions = []
    
        for row in rows:
            pending_transactions = []
            # Prepare recurring for display
            temp_recurring_display = self._row_to_display(row) 
            temp_recurring = temp_recurring_display.recurring

            # Get existing dates in transaction repo for recurring
            existing_dates = {cast_str_to_datetime(d) for d in self.transaction_repo.get_dates_for_recurring(temp_recurring.id)}

            # Get limit date for recurring - today of recurring end date
            limit_date = min(today, cast_str_to_datetime(temp_recurring.end_date)) if temp_recurring.end_date else today

            # Set occurence date as next due date
            occurrence_date = cast_str_to_datetime(temp_recurring.next_due_date)

            # Create new transactions between due date and limit date if it was not already created
            while occurrence_date <= limit_date:
                if occurrence_date not in existing_dates:
                        transaction = Transaction(
                            wallet_id=temp_recurring.wallet_id,
                            category_id=temp_recurring.category_id,
                            title=temp_recurring.title,
                            description=temp_recurring.description,
                            date=occurrence_date,
                            operation_type=temp_recurring.operation_type,
                            amount=temp_recurring.amount,
                            merchant=temp_recurring.merchant,
                            recurring_id=temp_recurring.id,
                        )
                        pending_transactions.append(transaction)
                occurrence_date = self._calculate_next_date(occurrence_date, temp_recurring.recurrence_interval)

            if pending_transactions:
                temp_recurring_display.occurrences = pending_transactions
                due_transactions.append(temp_recurring_display)

        return due_transactions
    
    def get_due_count(self, wallet_id: int, today: datetime | None = None) -> int: 
        """Get due transaction count for display"""
        today = today or datetime.today()
        count = self.recurring_transaction_repo.get_due_count(
            wallet_id=wallet_id,
            today=today
        )
        return count

    # Write methods
    def toggle_active(self, recurring_id: int) -> None:
        """Activate or diactive recurring transaction"""
        self.recurring_transaction_repo.toggle_active(recurring_id=recurring_id)

        self.app_state.emit_recurring_transaction_change()


    def confirm_transactions(self, transactions: list[Transaction]):
        """Confirm transactions"""
        with self.transaction_repo.db.transaction():
            for transaction in transactions:
                transaction.date = cast_datetime_to_str(transaction.date, format="%Y-%m-%d")
                self.transaction_repo.create_no_commit(transaction)
        
        self.app_state.emit_transaction_change()


    def delete_transactions(self, ids: list[int]):
        """Method for deleting selected recurring transaction from database"""

        self.recurring_transaction_repo.delete_many(ids=ids)

        self.app_state.emit_recurring_transaction_change()


    def is_over_due(self, next_due_date:str) -> bool:
        """Check if specified date is due"""
        next_due_date = cast_str_to_datetime(next_due_date)
        if next_due_date <= datetime.today():
            return True
        return False
    
    # Helpers
    def _row_to_display(self, row: tuple) -> RecurringTransactionDisplay:
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
                

    def advance_recurrings(self, recurrings: list[RecurringTransactionDisplay], confirmed: list[Transaction]):
        """Advance recurring transaction"""

        # Advance each recurring based on what was confirmed
        confirmed_dates_by_recurring = {}
        for t in confirmed:
            confirmed_dates_by_recurring.setdefault(t.recurring_id, set()).add(t.date)

        for group in recurrings:
            recurring = group.recurring
            confirmed_dates = confirmed_dates_by_recurring.get(recurring.id, set())

            # Earliest occurrence NOT confirmed
            unconfirmed = [
                occ.date for occ in group.occurrences
                if occ.date not in confirmed_dates
            ]

            if unconfirmed:
                # Floor stays at earliest unconfirmed → it reappears next launch
                recurring.next_due_date = cast_datetime_to_str(min(unconfirmed), format="%Y-%m-%d")
            else:
                # All confirmed → advance to first future date
                next_date = cast_str_to_datetime(recurring.next_due_date)
                today_iso = datetime.today()
                
                while next_date <= today_iso:
                    next_date = self._calculate_next_date(next_date, recurring.recurrence_interval)
                if recurring.end_date and next_date > cast_str_to_datetime(recurring.end_date):
                    recurring.is_active = False
                recurring.next_due_date = cast_datetime_to_str(next_date, format="%Y-%m-%d")


            self.recurring_transaction_repo.update(recurring)

        self.app_state.emit_recurring_transaction_change()