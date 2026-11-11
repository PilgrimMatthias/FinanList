from app.database.repositories import UserRepo, UserProfileRepo
from app.database.models import UserProfile, User
from app.core.app_state import AppState
from app.core.enums import Currency
from .models import ProfileSummary
from app.core.exceptions import ValidationError

class ProfileService:
    def __init__(
        self,
        user_repo: UserRepo,
        user_profile_repo: UserProfileRepo,
        app_state: AppState
    ):
        self.user_repo = user_repo
        self.user_profile_repo = user_profile_repo
        self.app_state = app_state

    def get_user(self, user_id: int) -> User:
        """Returns user"""
        return self.user_repo.get_user_by_id(id=user_id)

    def get_user_profile(self, user_id:int) -> UserProfile:
        """Returns user profile"""
        return self.user_profile_repo.get_by_user_id(user_id=user_id)

    def update_profile(self, user_id:int, name:str, currency: Currency) -> None:
        """
        Update user and user profile with new values

        Args:
            user_id (int): id of user
            name (str): user name
            net (float): net income
            gross (float): gross income
            expenses (float): expenses monthly
            currency (Currency): currency

        Raises:
            ValidationError: Name is required
            ValidationError: Any value can not be negative
        """
        if not name.strip():
            raise ValidationError("Name is required!")

        user = self.get_user(user_id = user_id)
        user_profile = self.get_user_profile(user_id = user_id)

        user.name = name.strip()
        user_profile.currency = currency

        with self.user_repo.db.transaction():
            self.user_repo.update_no_commit(user = user)
            self.user_profile_repo.update_no_commit(user_profile=user_profile)

        self.app_state.emit_user_change() 