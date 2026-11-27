from app.core import AppState
from app.database.repositories import (
    WalletRepo,
    CategoryRepo,
    TransactionRepo,
    RecurringTransactionRepo,
)
from app.database.models import Wallet, Category
from app.core.enums import Currency, OperationType
from app.core.exceptions import ValidationError
from app.core.constants import DEFAULT_MAIN_CATEGORIES, DEFAULT_SUB_CATEGORIES
from .models import WalletSummary, PlanSuggestion
from datetime import date
from app.core.utils import month_window

# Everything that leaves the wallet, used when averaging scheduled outflow.
OUTFLOW_TYPES = [
    OperationType.EXPENSE,
    OperationType.SAVING,
    OperationType.INVESTMENT,
]


class WalletService:
    """Wallet service"""

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

    def get_all_wallets(self, user_id: int) -> list[Wallet]:
        """Returns all wallets for user"""
        return self.wallet_repo.get_by_user_id(user_id=user_id)

    def get_balance(self, wallet_id: int) -> float:
        """Returns balance for wallet"""
        return self.wallet_repo.get_balance(wallet_id=wallet_id)

    def get_delete_impact(self, wallet_id: int) -> dict:
        """Returns deletion impact for wallet"""
        return {
            "categories": self.category_repo.count_by_wallet_id(wallet_id),
            "transactions": self.transaction_repo.count_by_wallet_id(wallet_id),
            "recurring": self.recurring_transaction_repo.count_by_wallet_id(wallet_id),
        }

    def get_wallet(self, wallet_id: int) -> Wallet:
        """Returns one wallet"""
        return self.wallet_repo.get_by_id(id=wallet_id)

    def _seed_default_categories(self, wallet_id: int):
        """Create default categories for wallet"""
        for main_category in DEFAULT_MAIN_CATEGORIES:
            temp_main_category = Category(
                wallet_id=wallet_id,
                name=main_category,
                operation_type=OperationType.EXPENSE,
            )
            temp_main_category = self.category_repo.create(temp_main_category)

            for sub_category in DEFAULT_SUB_CATEGORIES:
                temp_sub_category = Category(
                    wallet_id=wallet_id,
                    name=sub_category,
                    operation_type=OperationType.EXPENSE,
                    parent_id=temp_main_category.id,
                )
                temp_sub_category = self.category_repo.create(temp_sub_category)

            if main_category == "Private":
                temp_sub_category = Category(
                    wallet_id=wallet_id,
                    name="Income",
                    operation_type=OperationType.INCOME,
                    parent_id=temp_main_category.id,
                )
                temp_sub_category = self.category_repo.create(temp_sub_category)

        # Uncathegorized category
        temp_sub_category = Category(
            wallet_id=wallet_id,
            name="Uncategorized",
            operation_type=OperationType.EXPENSE,
            is_protected=True,
        )
        temp_sub_category = self.category_repo.create(temp_sub_category)

    def create_wallet(
        self,
        user_id: int,
        name: str,
        currency: Currency,
        initial_balance: float,
        net_salary_monthly: float,
        everyday_spending_monthly: float,
    ) -> Wallet:
        """Creates wallet in database"""
        # Validation
        if not name.strip():
            raise ValidationError("Name is required")
        if currency is None:
            raise ValidationError("Currency is required")
        if currency not in Currency:
            raise ValidationError("Currency must be valid")

        # Define wallet
        wallet = Wallet(
            user_id=user_id,
            name=name,
            currency=currency,
            initial_balance=initial_balance,
            net_salary_monthly=net_salary_monthly,
            everyday_spending_monthly=everyday_spending_monthly,
        )

        wallet = self.wallet_repo.create(wallet=wallet)

        self._seed_default_categories(wallet.id)

        self.app_state.wallet_changed.emit(wallet.id)

        return wallet

    def update_wallet(self, wallet: Wallet):
        """Updates wallet"""
        # Validation
        if not wallet.name.strip():
            raise ValidationError("Name is required")

        wallet_in_db = self.wallet_repo.get_by_id(id=wallet.id)
        if wallet_in_db.currency != wallet.currency:
            raise ValidationError("Currency can not be changed!")

        wallet = self.wallet_repo.update(wallet=wallet)
        self.app_state.wallet_changed.emit(wallet.id)

    def delete_wallet(self, wallet_id: int):
        """Deletes wallet by id"""
        if self.app_state.active_wallet_id == wallet_id:
            raise ValidationError("Wallet is active! Can not delete active wallet!")

        self.wallet_repo.delete_by_id(wallet_id=wallet_id)
        self.app_state.wallet_changed.emit(wallet_id)

    def set_active_wallet(self, wallet_id: int):
        """Sets choosen wallet as active"""
        wallet = self.wallet_repo.get_by_id(id=wallet_id)

        if wallet is None:
            raise ValidationError("Wallet does not exists!")
        if wallet.user_id != self.app_state.active_user_id:
            raise ValidationError("Wallet does not belong to current user!")

        self.app_state.set_active_wallet(wallet_id=wallet_id)

    def calculate_summary(
        self,
        net: float | None,
        everyday: float | None,
        recurring_outflow: float | None,
    ) -> WalletSummary:
        """
        Returns calculated wallet summary

        everyday is only the non-scheduled part of spending, so the scheduled
        side has to come back in or "Left each month" would ignore every bill.

        Args:
            net (float): net income monthly
            everyday (float): everyday spending monthly, excluding scheduled items
            recurring_outflow (float): average monthly total of scheduled bills
                and transfers, from get_recurring_outflow()

        Returns:
            WalletSummary: wallet summary for display
        """

        net = net or 0.0
        everyday = everyday or 0.0
        recurring_outflow = recurring_outflow or 0.0

        left = net - everyday - recurring_outflow
        return WalletSummary(
            left_each_month=left,
            savings_rate=left / net if net else None,
        )

    def get_months_of_history(self, wallet_id: int, today: date = None) -> int:
        """Complete months between the first transaction and this month.

        A month with no transactions still counts - the user genuinely spent
        nothing. Months before the first transaction do not, because the
        wallet had no history to average.
        """
        first = self.transaction_repo.get_first_transaction_date(wallet_id)
        if first is None:
            return 0

        today = today or date.today()
        first_date = date.fromisoformat(first[:10])
        return (today.year - first_date.year) * 12 + (today.month - first_date.month)

    def get_recurring_outflow(
        self, wallet_id: int, months: int, today: date = None
    ) -> float:
        """Average monthly outflow from scheduled items.

        Bills, savings and investments that came from a recurring transaction.
        Used by calculate_summary, which otherwise only sees everyday spending.
        """
        available = self.get_months_of_history(wallet_id, today)
        if available == 0:
            return 0.0

        counted = min(months, available)
        date_from, date_to = month_window(counted, today)

        total = self.transaction_repo.sum_by_type(
            wallet_id,
            OUTFLOW_TYPES,
            date_from,
            date_to,
            recurring=True,
        )
        return total / counted

    def get_plan_suggestion(
        self,
        wallet_id: int,
        months: int,
        today: date = None,
    ) -> PlanSuggestion | None:
        """Derived averages for the calibration hints.

        PlanSuggestion.expenses is EVERYDAY spending - expenses with no
        recurring link. Scheduled bills are excluded because the forecast adds
        them separately; including them here would double-count.
        """
        available = self.get_months_of_history(wallet_id, today)
        if available == 0:
            return None

        counted = min(months, available)
        date_from, date_to = month_window(counted, today)

        income = self.transaction_repo.sum_by_type(
            wallet_id, [OperationType.INCOME], date_from, date_to
        )

        everyday = self.transaction_repo.sum_by_type(
            wallet_id,
            [OperationType.EXPENSE],
            date_from,
            date_to,
            recurring=False,
        )

        return PlanSuggestion(
            income=income / counted,
            expenses=everyday / counted,
            months_counted=counted,
        )
