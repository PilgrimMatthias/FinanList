from app.core import AppState
from app.database.repositories import (
    WalletRepo,
    CategoryRepo,
    TransactionRepo,
    RecurringTransactionRepo,
)
from app.database.models import Wallet
from app.core.enums import Currency
from app.core.exceptions import ValidationError


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
        categories_count = len(self.category_repo.get_by_wallet_id(wallet_id=wallet_id))
        transaction_count = len(
            self.transaction_repo.get_by_wallet_id(wallet_id=wallet_id)
        )
        rec_transaction_count = len(
            self.recurring_transaction_repo.get_by_wallet_id(wallet_id=wallet_id)
        )

        impact_dict = {
            "categories": categories_count,
            "transactions": transaction_count,
            "recurring": rec_transaction_count,
        }

        return impact_dict

    def create_wallet(
        self, user_id: int, name: str, currency: Currency, initial_balance: float
    ) -> Wallet:
        """Creates wallet in database"""
        # Validation
        if not name.strip():
            raise ValidationError("Name is required")
        if currency is not None and currency in Currency:
            raise ValidationError("Currency must be valid")

        # Define wallet
        wallet = Wallet(
            user_id=user_id,
            name=name,
            currency=currency,
            initial_balance=initial_balance,
        )

        self.wallet_repo.create(wallet=wallet)

        self.app_state.wallet_changed.emit()

    def update_wallet(self, wallet: Wallet):
        """Updates wallet"""
        # Validation
        if not wallet.name.strip():
            raise ValidationError("Name is required")

        wallet_in_db = self.wallet_repo.get_by_id(id=wallet.id)
        if wallet_in_db.currency != wallet.currency:
            raise ("Currency can not be changed!")

        self.wallet_repo.update(wallet=wallet)
        self.app_state.wallet_changed.emit()

    def delete_wallet(self, wallet_id: int):
        """Deletes wallet by id"""
        if self.app_state.active_wallet_id == wallet_id:
            raise ("Wallet is active! Can not delete active wallet!")

        self.wallet_repo.delete_by_id(wallet_id=wallet_id)
        self.app_state.wallet_changed.emit()

    def set_active_wallet(self, wallet_id: int):
        """Sets choosen wallet as active"""
        wallet = self.wallet_repo.get_by_id(id=wallet_id)

        if wallet is None:
            raise ("Wallet does not exists!")
        if wallet.user_id != self.app_state.active_user_id:
            raise ("Wallet does not belong to current user!")

        self.app_state.set_active_wallet(wallet_id=wallet_id)
        self.app_state.wallet_changed.emit()
