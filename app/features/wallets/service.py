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
        self, user_id: int, name: str, currency: Currency, initial_balance: float
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
