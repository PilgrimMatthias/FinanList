from .analysis.view import AnalysisView
from .dashboard.view import DashboardView
from .history.view import HistoryView
from .investments.view import InvestmentView
from .savings.view import SavingsView
from .settings.view import SettingsView
from .upcoming.view import UpcomingView
from .wallets.view import WalletsView
from .categories.view import CategoriesView
from .profile.view import ProfileView
from .auth import AuthView, AuthService

__all__ = [
    "AnalysisView",
    "DashboardView",
    "HistoryView",
    "InvestmentView",
    "SavingsView",
    "SettingsView",
    "UpcomingView",
    "CategoriesView",
    "WalletsView",
    "ProfileView",
    "AuthView",
    "AuthService",
]
