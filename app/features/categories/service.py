from app.core import AppState
from app.database.repositories import (
    WalletRepo,
    CategoryRepo,
    TransactionRepo,
    RecurringTransactionRepo,
)
from app.database import Category, Wallet
from app.core.enums import OperationType
from app.core.exceptions import ValidationError


class CategoryService:
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

    # def get_active_wallet(self) -> Wallet:
    #     """Method to get active wallet"""
    #     return self.wallet_repo.get_by_id(self.app_state.active_wallet_id)

    def get_all_main_dialog_categories(self, wallet_id: int) -> list[Category]:
        """Method to get all main categories for the wallet"""
        categories = self.category_repo.get_main_categories(wallet_id=wallet_id)
        return [c for c in categories if self._should_display(c) if not c.is_protected]

    def get_all_main_categories(self, wallet_id: int) -> list[Category]:
        """Method to get all main categories for the wallet"""
        categories = self.category_repo.get_main_categories(wallet_id=wallet_id)
        return [c for c in categories if self._should_display(c)]

    def _should_display(self, category: Category) -> bool:
        """Check if category should be displayed for user"""
        if not category.is_protected:
            return True
        # Protected — show if it (or its subs) has transactions
        return self._has_any_transactions(category)

    def _has_any_transactions(self, category: Category) -> bool:
        """Check category if it has any transactions assigned to it"""
        # Check main
        if self.transaction_repo.exists_by_category(category.id):
            return True
        if self.recurring_transaction_repo.exists_by_category(category.id):
            return True

        # Check subcategories
        subs = self.category_repo.get_subcategories(category.id)
        for sub in subs:
            if self.transaction_repo.exists_by_category(sub.id):
                return True
            if self.recurring_transaction_repo.exists_by_category(sub.id):
                return True
        return False

    def get_all_subcategories(self, parent_id: int) -> list[Category]:
        """Method to get all sub categories for the wallet"""
        subs = self.category_repo.get_subcategories(parent_id=parent_id)
        return [s for s in subs if self._should_display(s)]

    def get_affected_transaction_count(self, category_ids: list[int]) -> int:
        """Method to get number of affected transactions for operation on categories"""
        count = 0
        for cat_id in category_ids:
            category = self.category_repo.get_by_id(cat_id)

            # Direct transactions on this category
            count += self.transaction_repo.count_by_category(cat_id)
            count += self.recurring_transaction_repo.count_by_category(cat_id)

            # If main category, also count subcategory transactions
            if category.parent_id is None:
                for sub in self.category_repo.get_subcategories(cat_id):
                    count += self.transaction_repo.count_by_category(sub.id)
                    count += self.recurring_transaction_repo.count_by_category(sub.id)

        return count

    def _category_name_taken(self, name: str, wallet_id: int) -> bool:
        """Check if category exists in database

        Returns:
            bool: True if exists.
        """
        category_check = self.category_repo.get_by_name_and_wallet(
            name=name, wallet_id=wallet_id
        )

        if category_check is not None:
            return True

        return False

    def _is_subcategory(self, category_id: int) -> bool:
        """
        Check if parent id is actually sub category.

        Returns:
            bool: True if parent id already is sub category
        """
        category = self.category_repo.get_by_id(category_id)
        return category is not None and category.parent_id is not None

    def create_category(
        self,
        wallet_id: int,
        name: str,
        color: str = None,
        parent_id: int = None,
        operation_type: OperationType = None,
    ):
        # Validation
        if name is None or name.strip() == "":
            raise ValidationError("Name must not be empty")

        if parent_id is None and operation_type is None:
            raise ValidationError("Main category must contain operation type")
        if parent_id is not None and operation_type is None:
            raise ValidationError("Subcategory must have operation type")

        if parent_id is None:
            # Main category: check name unique across mains in this wallet
            existing = self.category_repo.get_by_name_and_wallet(name, wallet_id)
            if existing and existing.parent_id is None:
                raise ValidationError(f"Main category '{name}' already exists")
        else:
            # Sub category: check name unique under this parent
            siblings = self.category_repo.get_subcategories(parent_id)
            if any(s.name == name for s in siblings):
                raise ValidationError(
                    f"Subcategory '{name}' already exists under this category"
                )

        if parent_id is not None and self._is_subcategory(parent_id):
            raise ValidationError("Creating nested category is not allowed")

        new_category = Category(
            wallet_id=wallet_id,
            parent_id=parent_id,
            name=name,
            operation_type=operation_type,
            color=color,
        )
        self.category_repo.create(category=new_category)

        self.app_state.emit_categories_change()

    def update_category(self, category: Category):
        """Update category"""
        self.category_repo.update(category=category)

        self.app_state.emit_categories_change()

    def delete_categories(self, category_ids: list[int]):
        """Method for category deletion

        During deletion all transactions from deleted category are getting it's category reassigned to uncategorized category
        """
        # Validation
        for cat_id in category_ids:
            category = self.category_repo.get_by_id(cat_id)
            if category is None:
                raise ValidationError(f"Category {cat_id} not found")
            if category.is_protected:
                raise ValidationError(
                    f"Cannot delete protected category '{category.name}'"
                )

        # Get uncategorized category (create if not exists) and its subcategory for reassignment
        uncategorized = self.ensure_uncategorized_exists(
            self.app_state.active_wallet_id
        )
        uncategorized_sub = self._ensure_uncategorized_sub_exists(uncategorized)

        for cat_id in category_ids:
            category = self.category_repo.get_by_id(cat_id)

            if category.parent_id is None:
                # Main category — reassign all subs' transactions first
                for sub in self.category_repo.get_subcategories(cat_id):
                    self.transaction_repo.reassign_category(
                        sub.id, uncategorized_sub.id
                    )
                    self.recurring_transaction_repo.reassign_category(
                        sub.id, uncategorized_sub.id
                    )
            else:
                # Sub category — reassign its own transactions
                self.transaction_repo.reassign_category(cat_id, uncategorized_sub.id)
                self.recurring_transaction_repo.reassign_category(
                    cat_id, uncategorized_sub.id
                )

            self.category_repo.delete_by_id(cat_id)

        self.app_state.emit_categories_change()
        self.app_state.emit_transaction_change()
        self.app_state.emit_recurring_transaction_change()

    def ensure_uncategorized_exists(self, wallet_id: int):
        """Ensure that uncategorized category exists in db - if not create it"""
        uncategorized_category = self.category_repo.get_by_name_and_wallet(
            name="Uncategorized", wallet_id=wallet_id
        )

        if uncategorized_category is None:
            uncategorized_category = Category(
                wallet_id=wallet_id,
                name="Uncategorized",
                operation_type=OperationType.EXPENSE,
                is_protected=True,
            )
            uncategorized_category = self.category_repo.create(uncategorized_category)

        return uncategorized_category

    def _ensure_uncategorized_sub_exists(self, parent: Category) -> Category:
        """Ensure Uncategorized has a subcategory for transaction reassignment."""
        subs = self.category_repo.get_subcategories(parent.id)
        for sub in subs:
            if sub.name == "Uncategorized" and sub.is_protected:
                return sub

        # Create it
        new_sub = Category(
            wallet_id=parent.wallet_id,
            parent_id=parent.id,
            name="Uncategorized",
            operation_type=OperationType.EXPENSE,
            is_protected=True,
        )
        return self.category_repo.create(new_sub)
