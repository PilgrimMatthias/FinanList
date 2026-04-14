from app.core import AppState
from app.database.repositories import (
    UserRepo,
    UserProfileRepo,
    WalletRepo,
    CategoryRepo,
)
from app.database import User, UserProfile, Wallet, Category

from app.core.enums import Currency, OperationType
from app.core.constants import DEFAULT_MAIN_CATEGORIES, DEFAULT_SUB_CATEGORIES
from app.core.exceptions import ValidationError


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        profile_repo: UserProfileRepo,
        wallet_repo: WalletRepo,
        category_repo: CategoryRepo,
        app_state: AppState,
    ):
        super().__init__()

        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.wallet_repo = wallet_repo
        self.category_repo = category_repo
        self.app_state = app_state

    def get_all_users(self) -> list[User]:
        """Method to get all users from database"""
        return self.user_repo.get_all()

    def create_user(
        self,
        name: str,
        gross_salary_monthly: float = 0,
        net_salary_monthly: float = 0,
        estimated_expenses_monthly: float = 0,
        initial_balance: float = 0,
        currency: Currency = Currency.PLN,
    ):
        """Create new user with it's own profile and first wallet"""

        # Validation
        if gross_salary_monthly < 0:
            raise ValidationError("Gross salary (monthly) must equel or higher than 0")
        if net_salary_monthly < 0:
            raise ValidationError("Net salary (monthly) must equel or higher than 0")
        if estimated_expenses_monthly < 0:
            raise ValidationError(
                "Estimated expenses (monthly) must equel or higher than 0"
            )
        if initial_balance < 0:
            raise ValidationError("Inittial balance must equel or higher than 0")

        # Create new user
        new_user = User(name=name)
        new_user = self.user_repo.create(user=new_user)

        # Create new user profile
        new_user_profile = UserProfile(
            user_id=new_user.id,
            gross_salary_monthly=gross_salary_monthly,
            net_salary_monthly=net_salary_monthly,
            estimated_expenses_monthly=estimated_expenses_monthly,
        )
        new_user_profile = self.profile_repo.create(profile=new_user_profile)

        # Create first wallet
        new_wallet = Wallet(
            user_id=new_user.id,
            name="Private Wallet",
            currency=currency,
            initial_balance=initial_balance,
        )
        new_wallet = self.wallet_repo.create(wallet=new_wallet)

        for main_category in DEFAULT_MAIN_CATEGORIES:
            temp_main_category = Category(
                wallet_id=new_wallet.id,
                name=main_category,
                operation_type=OperationType.EXPENSE,
            )
            temp_main_category = self.category_repo.create(temp_main_category)

            for sub_category in DEFAULT_SUB_CATEGORIES:
                temp_sub_category = Category(
                    wallet_id=new_wallet.id,
                    name=sub_category,
                    operation_type=OperationType.EXPENSE,
                    parent_id=temp_main_category.id,
                )
                temp_sub_category = self.category_repo.create(temp_sub_category)

            if main_category == "Private":
                temp_sub_category = Category(
                    wallet_id=new_wallet.id,
                    name="Income",
                    operation_type=OperationType.INCOME,
                    parent_id=temp_main_category.id,
                )
                temp_sub_category = self.category_repo.create(temp_sub_category)

        # Uncathegorized category
        temp_sub_category = Category(
            wallet_id=new_wallet.id,
            name="Uncategorized",
            operation_type=OperationType.EXPENSE,
            is_protected=True,
        )
        temp_sub_category = self.category_repo.create(temp_sub_category)

        # Update state
        self.app_state.set_active_user(user_id=new_user.id)
        self.app_state.set_active_wallet(wallet_id=new_wallet.id)

    def select_user(self, user_id: int):
        """Select currently active user"""
        self.app_state.set_active_user(user_id=user_id)

        wallets = self.wallet_repo.get_by_user_id(user_id)
        if wallets:
            self.app_state.set_active_wallet(wallet_id=wallets[0].id)

    def check_auto_login(self):
        """Check if user is single and/or has auto login -> if yes user is automatically logged in"""
        users = self.get_all_users()

        if len(users) == 1:
            self.select_user(users[0].id)
