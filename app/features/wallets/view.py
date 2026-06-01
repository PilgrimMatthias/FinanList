from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QScrollArea,
    QFrame,
)
from app.core import show_error, show_confirmation, HLine

from .service import WalletService
from .widgets.wallet_card import WalletCard
from app.core.app_state import AppState
from app.core.exceptions import ValidationError
from app.database.models import Wallet
from app.config import WALLET_WINDOW_WIDTH, WALLET_WINDOW_HEIGHT
from .widgets.wallet_buttons import WalletButton
from .widgets.wallet_form_dialog import WalletFormDialog


class WalletsView(QDialog):
    """# Wallets view

    Displayes all wallets for current user and add button which give option to create new wallet.
    """

    def __init__(self, service: WalletService, app_state: AppState, parent=None):
        super().__init__(parent=parent)

        self.service = service
        self.app_state = app_state

        self._wallet_cards = []

        self._init_view()

        self.app_state.wallet_changed.connect(self._reload)

    def _init_view(self):
        """Initialize view"""
        self.setFixedWidth(WALLET_WINDOW_WIDTH)
        self.setFixedHeight(WALLET_WINDOW_HEIGHT)

        self.title_label = QLabel(self)
        self.title_label.setText("Wallets")
        self.title_label.setObjectName("transactionLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep_line = HLine()
        sep_line.setContentsMargins(10, 0, 10, 0)

        # Wallet cards
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        wallet_cards_widget = QWidget(self)

        self.scroll_area.setWidget(wallet_cards_widget)

        self.wallet_cards_layout = QVBoxLayout(wallet_cards_widget)
        self.wallet_cards_layout.setSpacing(5)
        self.wallet_cards_layout.setContentsMargins(5, 0, 5, 0)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 10, 5, 10)

        self.add_btn = WalletButton(
            text="+ Add Wallet",
            variant="add_wallet",
            height=50,
            width=WALLET_WINDOW_WIDTH - 20,
            on_click=self._show_wallet_dialog,
        )

        # Add widgets
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(sep_line)
        main_layout.addWidget(self.scroll_area)
        # main_layout.addStretch()
        main_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Reloading views
    def _reload(self, wallet_id: int = None):
        """Reload view method

        Clears current layout and then creates all the cards for user walets.
        """
        self._clear()  # clear view
        self._wallet_cards = []

        # Get user wallets
        user_wallets = self.service.get_all_wallets(
            user_id=self.app_state.active_user_id
        )

        # Create cards
        for wallet in user_wallets:
            temp_card = WalletCard(
                wallet=wallet,
                is_active=wallet.id == self.app_state.active_wallet_id,
                balance=self.service.get_balance(wallet_id=wallet.id),
                is_only_wallet=len(user_wallets) == 1,
            )

            temp_card.edit_requested.connect(self._show_wallet_dialog)
            temp_card.delete_requested.connect(self._on_delete_wallet)
            temp_card.set_active_requested.connect(self._set_wallet_as_active)

            self._wallet_cards.append(temp_card)
            self.wallet_cards_layout.addWidget(temp_card)
        self.wallet_cards_layout.addStretch()

    def _clear(self):
        """Remove all wallet cards from the layout."""
        while self.wallet_cards_layout.count():
            item = self.wallet_cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def showEvent(self, event):
        super().showEvent(event)
        self._reload()

    # Wallet operations
    def _show_wallet_dialog(self, wallet: Wallet = None):
        """Show wallet dialog for create/edit"""
        wallet_dialog = WalletFormDialog(
            service=self.service, wallet=wallet, parent=self
        )
        wallet_dialog.show()

    def _set_wallet_as_active(self, wallet: Wallet):
        """Set wallet as active"""
        if wallet:
            self.service.set_active_wallet(wallet_id=wallet.id)

    def _on_delete_wallet(self, wallet: Wallet):
        """On delete method for deletion of wallet"""
        if wallet.id == self.app_state.active_wallet_id:
            show_error(
                self, "Cannot delete the active wallet. Switch to another wallet first."
            )
            return

        impact = self.service.get_delete_impact(wallet.id)
        message = (
            f'This will permanently delete "{wallet.name}" and all its data:\n\n'
            f'• {impact["transactions"]} transactions\n'
            f'• {impact["recurring"]} recurring transactions\n'
            f'• {impact["categories"]} categories\n\n'
            f"This action cannot be undone."
        )

        if show_confirmation(
            self, message, title="Delete wallet", confirm_text="Delete wallet"
        ):
            try:
                self.service.delete_wallet(wallet.id)
            except ValidationError as e:
                show_error(self, str(e))
