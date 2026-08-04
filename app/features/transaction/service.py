from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.core import AppState
from app.database.repositories import (
    WalletRepo,
    CategoryRepo,
    TransactionRepo,
    RecurringTransactionRepo,
)
from app.database import Wallet, Category, Transaction, RecurringTransaction

from app.core.enums import OperationType, RecurrenceInterval
from app.core import set_next_due_date
from app.core.exceptions import ValidationError


class TransactionService:
    def __init__(
        self,
        wallet_repo: WalletRepo,
        category_repo: CategoryRepo,
        transaction_repo: TransactionRepo,
        recurring_transaction_repo: RecurringTransactionRepo,
        app_state: AppState,
    ):
        self.wallet_repo = wallet_repo
        self.category_repo = category_repo
        self.transaction_repo = transaction_repo
        self.recurring_transaction_repo = recurring_transaction_repo
        self.app_state = app_state

    def get_active_wallet(self) -> Wallet:
        """Method to get active wallet"""
        return self.wallet_repo.get_by_id(self.app_state.active_wallet_id)

    def get_wallet_by_id(self, id: int) -> Wallet:
        return self.wallet_repo.get_by_id(id)

    def get_all_wallets(self) -> list[Wallet]:
        """Method to get all wallets for the user"""
        return self.wallet_repo.get_by_user_id(self.app_state.active_user_id)

    def get_all_main_categories(self, wallet_id: int) -> list[Category]:
        """Method to get all main categories for the wallet"""
        return [
            category
            for category in self.category_repo.get_main_categories(wallet_id=wallet_id)
            if not category.is_protected
        ]

    def get_all_sub_categories(self, name: str, wallet_id=None) -> list[Category]:
        """Method to get all sub categories for the wallet"""
        parent = self.category_repo.get_by_name_and_wallet(
            name=name,
            wallet_id=wallet_id or self.app_state.active_wallet_id,
        )
        return [
            category
            for category in self.category_repo.get_subcategories(parent_id=parent.id)
            if not category.is_protected
        ]

    def get_main_category_by_id(self, sub_id: int) -> Category:
        """Method to get all sub categories for the wallet"""
        sub_category = self.category_repo.get_by_id(id=sub_id)
        main_category = self.category_repo.get_by_id(id=sub_category.parent_id)

        return main_category

    def get_sub_category_by_id(self, id: int) -> Category:
        """Method to get all sub categories for the wallet"""
        category = self.category_repo.get_by_id(id=id)
        return category

    def get_recurring_transaction_by_id(self, id: int) -> RecurringTransaction:
        return self.recurring_transaction_repo.get_by_id(id=id)

    def validate_start_date(
        self, start_date: datetime, interval: RecurrenceInterval
    ) -> datetime | None:
        """Returns corrected date if start_date is invalid, None if it's already valid."""
        if interval != RecurrenceInterval.DOES_NOT_REPEAT:

            now = datetime.now() + relativedelta(
                hour=0, minute=0, second=0, microsecond=0
            )

            if start_date <= now.date():
                return now

        return None
    
    def validate_end_date(self, start_date: datetime, end_date: datetime):
        """Returns corrected date if start_date is newer than end_date, end_date if it's lower."""

        if start_date >= end_date:
            return start_date

        return end_date

    def validate_send_date(self, start_date, end_date) -> datetime | None:
        """Returns corrected date if end_date is invalid, None if it's already valid."""
        if end_date < start_date:
            return start_date
        return None

    def create_transaction(
        self,
        wallet: Wallet,
        category_name: str,
        title: str,
        start_date: datetime,
        operation_type: OperationType,
        amount: float,
        description: str = None,
        merchant: str = None,
        repeat_interval: RecurrenceInterval = None,
        end_date: datetime | None = None,
    ):
        category = self.category_repo.get_by_name_and_wallet(
            name=category_name, wallet_id=wallet.id
        )

        # Validation
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if not title.strip():
            raise ValidationError("Title is required")
        if operation_type is None:
            raise ValidationError("Operation type must be choosen")

        if repeat_interval == RecurrenceInterval.DOES_NOT_REPEAT:
            self._create_one_time_transaction(
                wallet=wallet,
                category=category,
                title=title,
                description=description,
                start_date=start_date,
                operation_type=operation_type,
                merchant=merchant,
                amount=amount,
            )
        else:
            self._create_recurring_transaction(
                wallet=wallet,
                category=category,
                title=title,
                description=description,
                operation_type=operation_type,
                merchant=merchant,
                amount=amount,
                repeat_interval=repeat_interval,
                start_date=start_date,
                end_date=end_date,
            )

    def _create_one_time_transaction(
        self,
        wallet: Wallet,
        category: Category,
        title: str,
        start_date: datetime,
        operation_type: OperationType,
        amount: float,
        description: str = None,
        merchant: str = None,
    ):
        """Create one time transaction"""
        new_transaction = Transaction(
            wallet_id=wallet.id,
            category_id=category.id,
            title=title,
            description=description,
            date=start_date,
            operation_type=operation_type,
            merchant=merchant,
            amount=amount,
        )
        self.transaction_repo.create(transaction=new_transaction)

        self.app_state.emit_transaction_change()

    def _create_recurring_transaction(
        self,
        wallet: Wallet,
        category: Category,
        title: str,
        start_date: datetime,
        operation_type: OperationType,
        amount: float,
        description: str = None,
        merchant: str = None,
        repeat_interval: RecurrenceInterval = None,
        end_date: datetime | None = None,
    ):
        """Create recurring transaction

        If transaction start date is current date than automatically transaction is create
        and next due date is set with choosen interval
        """

        next_due_date = set_next_due_date(
            start_date=start_date, interval=repeat_interval
        )

        new_recurring_transaction = RecurringTransaction(
            wallet_id=wallet.id,
            category_id=category.id,
            title=title,
            description=description,
            operation_type=operation_type,
            merchant=merchant,
            amount=amount,
            recurrence_interval=repeat_interval,
            start_date=start_date,
            end_date= end_date if end_date is not None else None,
            next_due_date=next_due_date,
            is_active=True,
        )
        new_recurring_transaction = self.recurring_transaction_repo.create(
            recurring_transaction=new_recurring_transaction
        )
        self.app_state.emit_recurring_transaction_change()

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if start_date <= now.date():
            new_transaction = Transaction(
                wallet_id=wallet.id,
                category_id=category.id,
                title=title,
                description=description,
                date=start_date,
                operation_type=operation_type,
                merchant=merchant,
                amount=amount,
                recurring_id=new_recurring_transaction.id,
            )
            self.transaction_repo.create(transaction=new_transaction)

            self.app_state.emit_transaction_change()

    def _validate_update(self, transaction: Transaction | RecurringTransaction):
        if transaction.amount <= 0:
            raise ValidationError("Amount must be positive")
        if not transaction.title.strip():
            raise ValidationError("Title is required")

    def update_transaction(
        self,
        transaction: Transaction,
    ):
        self._validate_update(transaction=transaction)
        self.transaction_repo.update(transaction=transaction)

        self.app_state.emit_transaction_change()

    def update_recurring_transaction(
        self,
        transaction: RecurringTransaction,
    ):
        # update next due date
        transaction.next_due_date = set_next_due_date(
            start_date=transaction.start_date, interval=transaction.recurrence_interval
        )
        self._validate_update(transaction=transaction)
        self.recurring_transaction_repo.update(recurring_transaction=transaction)

        self.app_state.emit_recurring_transaction_change()
