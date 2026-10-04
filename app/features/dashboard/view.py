from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from .service import DashboardService
from app.core.app_state import AppState
from .widgets import BalanceTile, MonthTile, DueTile, CategoryBars, RecentOperationCard, UpcomingCard
from datetime import datetime
from app.features.upcoming.widgets.due_transaction_dialog import DueTransactionDialog


class DashboardView(QWidget):
    review_recent_signal = Signal()
    review_upcoming_signal = Signal()

    def __init__(
        self,
        service: DashboardService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.app_state = app_state

        self._due_count = 0

        self.app_state.user_changed.connect(self._reload)
        self.app_state.wallet_changed.connect(self._reload)
        self.app_state.transaction_changed.connect(self._reload)
        self.app_state.recurring_transaction_changed.connect(self._reload)


        self._init_view()

    def _init_view(self):
        # Welcome row
        welcome_row = QWidget(self)
        welcome_row_layout = QHBoxLayout(welcome_row)
        welcome_row_layout.setSpacing(5)
        welcome_row_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(self)
        self.name_label.setText("Hello")
        self.name_label.setObjectName("dashboardNameLabel")

        self.month_label = QLabel(self)
        self.month_label.setText(f"{datetime.today().strftime("%A, %d %B %Y")}".capitalize())
        self.month_label.setObjectName("dashboardDate")

        welcome_row_layout.addWidget(self.name_label)
        welcome_row_layout.addStretch()
        welcome_row_layout.addWidget(self.month_label)

        # Top row
        top_row = QWidget(self)
        top_row.setFixedHeight(125)
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setSpacing(5)
        top_row_layout.setContentsMargins(0, 0, 0, 0)

        self.balance_tile = BalanceTile()
        self.month_tile = MonthTile()
        self.due_tile = DueTile(due_count=self._due_count)
        self.due_tile.review_signal.connect(self._show_due_dialog)

        top_row_layout.addWidget(self.balance_tile,stretch=11)
        top_row_layout.addWidget(self.month_tile,stretch=13)
        top_row_layout.addWidget(self.due_tile,stretch=9)

        # Middle row
        middle_row = QWidget(self)
        middle_row.setFixedHeight(150)
        middle_row_layout = QHBoxLayout(middle_row)
        middle_row_layout.setSpacing(5)
        middle_row_layout.setContentsMargins(0, 0, 0, 0)

        self.category_bars = CategoryBars()

        middle_row_layout.addWidget(self.category_bars)

        # Bottom row
        bottom_row = QWidget(self)
        bottom_row.setFixedHeight(225)
        bottom_row_layout = QHBoxLayout(bottom_row)
        bottom_row_layout.setSpacing(5)
        bottom_row_layout.setContentsMargins(0, 0, 0, 0)

        self.recent_operations_card = RecentOperationCard()
        self.recent_operations_card.review_signal.connect(lambda: self.review_recent_signal.emit())
        self.upcomings_card = UpcomingCard()
        self.upcomings_card.review_signal.connect(lambda: self.review_upcoming_signal.emit())

        bottom_row_layout.addWidget(self.recent_operations_card, stretch=3)
        bottom_row_layout.addWidget(self.upcomings_card, stretch=2)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(welcome_row, stretch=0)
        main_layout.addWidget(top_row)
        main_layout.addWidget(middle_row)
        main_layout.addWidget(bottom_row, stretch=1)
        main_layout.addStretch()


    def _reload(self, wallet_id: int = None):
        """Full reload — model + UI"""
        if wallet_id is None or self.app_state._active_user_id is None:
            return

        # Get info for widgets
        user_name = self.service.get_user_name(user_id=self.app_state.active_user_id)
        wallet = self.service.get_wallet(wallet_id=wallet_id)
        balance = self.service.get_balance(wallet_id=wallet_id)
        today = datetime.today()
        current_month=self.service.get_current_month_name()

        month_summary = self.service.get_month_summary(
            wallet_id=wallet_id,
            year = today.year,
            month=today.month
        )
        categories_total = self.service.get_category_totals(
            wallet_id=wallet_id,
            year=today.year,
            month=today.month,
            top_n=3
        )

        recent_operations = self.service.get_recent(
            wallet_id = wallet_id,
            limit = 5
        )

        upcoming_operations = self.service.get_upcomings(
            wallet_id = wallet_id,
            limit = 5
        )

        # Update widgets
        self.name_label.setText(f"Hello, {user_name}")
        self.balance_tile.set_data(
            balance=balance,
            currency=wallet.currency,
            wallet_name=wallet.name
        )
        self.month_tile.set_data(
            current_month=current_month,
            month_summary=month_summary
        )

        self._due_count = self.service.get_due_count(wallet_id=wallet_id)

        self.due_tile.set_data(due_count=self._due_count)

        self.category_bars.set_data(
            categories_total = categories_total,
            currency = wallet.currency,
            month = current_month
        )

        self.recent_operations_card.set_data(transactions=recent_operations)

        self.upcomings_card.set_data(upcomings=upcoming_operations)

    def _show_due_dialog(self):
        """Shows due dialog to confirm transactions"""
    
        if self._due_count > 0:
            dialog = DueTransactionDialog(
                service=self.service.upcoming_service,
                parent=self,
            )
            dialog.exec()  
