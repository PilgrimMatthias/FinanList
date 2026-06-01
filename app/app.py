from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QStackedWidget,
    QScrollArea,
    QSizePolicy,
    QMenu,
    QWidgetAction,
)
from app.database.connection import Database
from app.database.repositories import (
    CategoryRepo,
    RecurringTransactionRepo,
    TransactionRepo,
    UserProfileRepo,
    UserRepo,
    WalletRepo,
)

from app.core import AppState, PushButton, center_window
from app.config import APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from app.features import (
    DashboardView,
    AnalysisView,
    HistoryView,
    HistoryService,
    InvestmentView,
    SavingsView,
    SettingsView,
    UpcomingView,
    WalletsView,
    WalletService,
    CategoriesView,
    CategoryService,
    ProfileView,
    AuthView,
    AuthService,
    TransactionView,
    TransactionService,
)


class MainWindow(QMainWindow):
    def __init__(self, database: Database):
        super().__init__()

        self.database = database
        self.app_state = AppState()

        self._init_services()
        self._init_ui()
        self._init_user_menu()

    def _init_services(self):
        """Create repos and services — single source of wiring."""
        # Repos
        self.user_repo = UserRepo(self.database)
        self.profile_repo = UserProfileRepo(self.database)
        self.wallet_repo = WalletRepo(self.database)
        self.category_repo = CategoryRepo(self.database)
        self.transaction_repo = TransactionRepo(self.database)
        self.recurring_repo = RecurringTransactionRepo(self.database)

        # Services
        self.auth_service = AuthService(
            user_repo=self.user_repo,
            profile_repo=self.profile_repo,
            wallet_repo=self.wallet_repo,
            category_repo=self.category_repo,
            app_state=self.app_state,
        )
        self.transaction_service = TransactionService(
            wallet_repo=self.wallet_repo,
            category_repo=self.category_repo,
            transaction_repo=self.transaction_repo,
            recurring_transaction_repo=self.recurring_repo,
            app_state=self.app_state,
        )
        self.category_service = CategoryService(
            wallet_repo=self.wallet_repo,
            category_repo=self.category_repo,
            transaction_repo=self.transaction_repo,
            recurring_transaction_repo=self.recurring_repo,
            app_state=self.app_state,
        )
        self.history_service = HistoryService(
            transaction_repo=self.transaction_repo, app_state=self.app_state
        )
        self.wallet_service = WalletService(
            wallet_repo=self.wallet_repo,
            category_repo=self.category_repo,
            transaction_repo=self.transaction_repo,
            recurring_transaction_repo=self.recurring_repo,
            app_state=self.app_state,
        )

        # Connect app state
        self.app_state.user_changed.connect(self.log_in)

    def _init_ui(self):
        """
        Initializes main window
        Window is displayed after sign in or user login (any user data exisits)
        """
        self.setWindowTitle(APP_NAME)
        center_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Top - level widget stack
        self.root_widget = QStackedWidget()
        self.setCentralWidget(self.root_widget)

        # Login view
        self.login_widget = AuthView(service=self.auth_service)
        self.root_widget.addWidget(self.login_widget)

        # Main content widget of the app
        self.main_widget = QWidget()
        main_layout = QHBoxLayout(self.main_widget)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(10)

        # User Name box
        self.user_box_btn = PushButton(
            text="USER", height=30, on_click=self.show_dropdown_menu
        )

        self.add_transaction_btn = PushButton(
            text="Add transaction", height=40, width=140, on_click=self.add_transaction
        )
        # self.add_transaction_btn.setIcon(QIcon(ADD_ICON))

        # Dashboard section
        self.dashboard_section_btn = PushButton(
            text="Dashboard",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(0),
        )

        # Analysis section
        self.analysis_section_btn = PushButton(
            text="Analysis",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(1),
        )
        # History section
        self.history_section_btn = PushButton(
            text="History",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(2),
        )

        # Upcoming section
        self.upcoming_section_btn = PushButton(
            text="Upcoming",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(3),
        )

        # Savings section
        self.savings_section_btn = PushButton(
            text="Savings",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(4),
        )

        # History section
        self.investment_section_btn = PushButton(
            text="Investment",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(5),
        )

        # Analysis section
        self.categories_section_btn = PushButton(
            text="Categories",
            height=35,
            width=140,
            on_click=lambda: self.set_current_section(6),
        )

        # Add widgets to layout
        self.sidebar_layout.addWidget(self.user_box_btn)
        self.sidebar_layout.addWidget(self.add_transaction_btn)
        self.sidebar_layout.addWidget(self.dashboard_section_btn)
        self.sidebar_layout.addWidget(self.analysis_section_btn)
        self.sidebar_layout.addWidget(self.history_section_btn)
        self.sidebar_layout.addWidget(self.upcoming_section_btn)
        self.sidebar_layout.addWidget(self.investment_section_btn)
        self.sidebar_layout.addWidget(self.savings_section_btn)
        self.sidebar_layout.addWidget(self.categories_section_btn)
        self.sidebar_layout.addStretch()

        # Scroll Area dla widżetu
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Główny layout contentu
        self.content = QWidget()
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        # Creating app sections
        self.dashboard_section = DashboardView()
        self.analysis_section = AnalysisView()
        self.history_section = HistoryView(
            service=self.history_service,
            transaction_service=self.transaction_service,
            app_state=self.app_state,
        )
        self.upcoming_section = UpcomingView()
        self.savings_section = SavingsView()
        self.investment_section = InvestmentView()
        self.categories_section = CategoriesView(
            service=self.category_service, app_state=self.app_state, parent=self
        )
        self.wallets_window = WalletsView(
            service=self.wallet_service, app_state=self.app_state, parent=self
        )
        self.settings_window = SettingsView()
        self.profile_window = ProfileView()

        # Stacked widgest for sections
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.addWidget(self.dashboard_section)
        self.stacked_pages.addWidget(self.analysis_section)
        self.stacked_pages.addWidget(self.history_section)
        self.stacked_pages.addWidget(self.upcoming_section)
        self.stacked_pages.addWidget(self.savings_section)
        self.stacked_pages.addWidget(self.investment_section)
        self.stacked_pages.addWidget(self.categories_section)

        self.content_layout.addWidget(self.stacked_pages)
        self.scroll_area.setWidget(self.content)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.scroll_area)

        self.root_widget.addWidget(self.main_widget)

        # Check for auto login
        self.auth_service.check_auto_login()

    def set_current_section(self, section_number: int = 0) -> None:
        self.stacked_pages.setCurrentIndex(section_number)

    def _init_user_menu(self):
        """
        Creation of user menu which is dropdown box with:
            - Account settings
            - App settings
        """
        self.user_menu = QMenu(self)
        self.user_menu.setObjectName("DropDownMenu")

        # Widget for holding buttons
        menu_widget = QWidget(self)
        layout = QVBoxLayout(menu_widget)

        # Account settings buttons
        self.profile_btn = PushButton(
            text="Profile",
            height=30,
            width=125,
            bg_color="#566876",
            bg_color_clicked="#899ba9",
            on_click=lambda: self.profile_window.show(),
        )

        # App settings button
        self.app_settings_btn = PushButton(
            text="App Settings",
            height=30,
            width=125,
            bg_color="#566876",
            bg_color_clicked="#899ba9",
            on_click=lambda: self.settings_window.show(),
        )

        # Wallets button
        self.wallet_btn = PushButton(
            text="Wallets",
            height=30,
            width=125,
            bg_color="#566876",
            bg_color_clicked="#899ba9",
            on_click=lambda: self.wallets_window.show(),
        )

        # Wallets button
        self.logout_btn = PushButton(
            text="Log out",
            height=30,
            width=125,
            bg_color="#566876",
            bg_color_clicked="#899ba9",
            on_click=self.log_out,
        )

        # Add buttons to the layout
        layout.addWidget(self.profile_btn)
        layout.addWidget(self.wallet_btn)
        layout.addWidget(self.app_settings_btn)
        layout.addWidget(self.logout_btn)

        # Create a QWidgetAction to add custom widgets to the QMenu
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(menu_widget)

        # Add the QWidgetAction to the dropdown menu
        self.user_menu.addAction(widget_action)

    def show_dropdown_menu(self):
        """
        Method to show dropdown user menu
        """
        # Show the dropdown menu under the main button
        self.user_menu.exec(
            self.user_box_btn.mapToGlobal(self.user_box_btn.rect().bottomLeft())
        )

    def add_transaction(self):
        dialog = TransactionView(parent=self, service=self.transaction_service)

        dialog.show()

    def log_in(self):
        self.root_widget.setCurrentIndex(1)

    def log_out(self):
        """
        Method used for showing window with user wallets.
        """
        self.user_menu.hide()
        self.app_state.set_active_user(None)
        self.app_state.set_active_wallet(None)
        self.root_widget.setCurrentIndex(0)
