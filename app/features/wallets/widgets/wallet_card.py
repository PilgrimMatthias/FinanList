from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from app.database.models import Wallet
from .wallet_buttons import WalletButton


class WalletCard(QFrame):
    """# Wallet card
    Wallet card for displaying base wallet information for user.
    Consists of information:
    - Name
    - Currency
    - Initial Balance

    If wallet is active then wallet will be displayed in color with information that it is active.

    """

    edit_requested = Signal(Wallet)
    delete_requested = Signal(Wallet)
    set_active_requested = Signal(Wallet)

    def __init__(
        self,
        wallet: Wallet,
        is_active: bool = False,
        balance: float = 0,
        is_only_wallet=False,
        parent=None,
    ):
        super().__init__(parent)

        self.wallet = wallet
        self._is_active = is_active
        self.balance = balance
        self.is_only_wallet = is_only_wallet

        self.setObjectName("walletCard")
        self.setProperty("active", str(self._is_active).lower())  # "true" or "false"

        self.init_card()

        self.style().unpolish(self)
        self.style().polish(self)

    def init_card(self):
        self.setMinimumHeight(140)

        # Top Frame
        top_widget = QWidget(self)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.wallet_state = QLabel(self)
        self.wallet_state.setText("ACTIVE WALLET" if self._is_active else "WALLET")
        self.wallet_state.setObjectName("walletCardMuted")

        top_layout.addWidget(self.wallet_state)
        top_layout.addStretch()
        if self._is_active:
            self.wallet_state_pill = QLabel(self)
            self.wallet_state_pill.setText("✓ Active")
            self.wallet_state_pill.setObjectName("walletActiveBadge")
            top_layout.addWidget(self.wallet_state_pill)

        self.name_label = QLabel(self)
        self.name_label.setText(self.wallet.name)
        self.name_label.setObjectName("walletCardName")

        # Bottom Frame
        bottom_widget = QWidget(self)
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.balance_label = self._create_balance_label()

        bottom_layout.addWidget(self.balance_label)
        bottom_layout.addStretch()

        # Active card — only Edit
        if self._is_active:
            self.edit_btn = WalletButton("Edit", variant="active_card", width=60)
            self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.wallet))
            bottom_layout.addWidget(
                self.edit_btn, alignment=Qt.AlignmentFlag.AlignBottom
            )

        # Inactive card — Set Active, Edit, Delete
        else:
            self.activate_btn = WalletButton("Set Active", variant="primary", width=90)
            self.activate_btn.clicked.connect(
                lambda: self.set_active_requested.emit(self.wallet)
            )

            self.edit_btn = WalletButton("Edit", variant="neutral", width=60)
            self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.wallet))

            bottom_layout.addWidget(
                self.activate_btn, alignment=Qt.AlignmentFlag.AlignBottom
            )
            bottom_layout.addWidget(
                self.edit_btn, alignment=Qt.AlignmentFlag.AlignBottom
            )
            if not self.is_only_wallet:
                self.delete_btn = WalletButton("Delete", variant="danger", width=60)
                self.delete_btn.clicked.connect(
                    lambda: self.delete_requested.emit(self.wallet)
                )

                bottom_layout.addWidget(
                    self.delete_btn, alignment=Qt.AlignmentFlag.AlignBottom
                )

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(top_widget)
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(bottom_widget)

    def _create_balance_label(self):
        """Create balance label with current balance and currency"""
        balance_widget = QWidget(self)
        balance_layout = QVBoxLayout(balance_widget)
        balance_layout.setContentsMargins(0, 0, 0, 0)

        balance_title_label = QLabel()
        balance_title_label.setText("Balance")
        balance_title_label.setObjectName("walletCardMuted")

        balance_value_widget = QWidget(self)
        balance_value_layout = QHBoxLayout(balance_value_widget)
        balance_value_layout.setContentsMargins(0, 0, 0, 0)

        balance_value_label = QLabel(self)
        balance_value_label.setText(
            f"{self.balance:,.2f}".replace(",", " ").replace(".", ",")
        )
        balance_value_label.setObjectName("walletCardBalance")

        currency_label = QLabel(self)
        currency_label.setText(self.wallet.currency.name)
        currency_label.setObjectName("walletCardCurrency")

        balance_value_layout.addWidget(balance_value_label)
        balance_value_layout.addWidget(
            currency_label, alignment=Qt.AlignmentFlag.AlignBottom
        )

        balance_layout.addWidget(balance_title_label)
        balance_layout.addWidget(balance_value_widget)

        return balance_widget
