from app.core import AppState
from app.database.repositories import (
    UserRepo,
    UserProfileRepo,
    WalletRepo,
)
from app.database import (
    User,
    UserProfile,
    Wallet,
)

from app.core.enums import Currency


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        profile_repo: UserProfileRepo,
        wallet_repo: WalletRepo,
        app_state: AppState,
    ):
        super().__init__()

        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.wallet_repo = wallet_repo
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

        # Update state
        self.app_state.set_active_user(user_id=new_user.id)
        self.app_state.set_active_wallet(wallet_id=new_wallet.id)

    def select_user(self, user_id: int):
        """Select currently active user"""
        self.app_state.set_active_user(user_id=user_id)

        wallets = self.wallet_repo.get_by_user_id(user_id)
        if wallets:
            self.app_state.set_active_wallet(wallet_id=wallets[0].id)
