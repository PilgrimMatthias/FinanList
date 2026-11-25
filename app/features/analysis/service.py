from app.core import AppState
from app.database.repositories import (
    RecurringTransactionRepo,
    TransactionRepo
)
from app.database.models import RecurringTransaction, Transaction
from app.core.utils import cast_str_to_datetime, cast_datetime_to_str
from datetime import datetime
from app.core.enums import Currency, RecurrenceInterval
from dateutil.relativedelta import relativedelta
from app.core.exceptions import ValidationError

class AnalysisService:
    def __init__(
        self,
        recurring_transaction_repo: RecurringTransactionRepo,
        transaction_repo: TransactionRepo,
        app_state: AppState,
    ):
        self.recurring_transaction_repo = recurring_transaction_repo
        self.transaction_repo = transaction_repo
        self.app_state = app_state


    def get_scheduled_occurences(self, wallet_id: int, start: datetime = None, end: datetime = datetime.today()) -> list[Transaction]:
        """Get due transactions for display"""
        # Get due recurrings
        today = today or datetime.today()
        rows = self.recurring_transaction_repo.get_active_by_wallet_id(
            wallet_id=wallet_id,
        )

        upcoming_transactions = []
    
        for row in rows:
            pending_transactions = []
            # Prepare recurring for display
            temp_recurring = RecurringTransaction.from_row(row)

            # Get existing dates in transaction repo for recurring
            existing_dates = {cast_str_to_datetime(d) for d in self.transaction_repo.get_dates_for_recurring(temp_recurring.id)}

            # Set occurence date as next due date
            occurrence_date = cast_str_to_datetime(temp_recurring.next_due_date)

            # Create new transactions between due date and limit date if it was not already created
            while start <= end:
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
                upcoming_transactions.append(pending_transactions)

        return upcoming_transactions