from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame
from app.core.enums import Currency
from app.core.utils import format_balance


class BalanceTile(QFrame):
    """
    Balnce Tile presents current wallet balance displayed as a card.
    """
    def __init__(self, balance:float = 0, currency:Currency = Currency.PLN, wallet_name:str = "Wallet", parent=None):
        super().__init__(parent=parent)
        self.balance = balance
        self.currency = currency
        self.wallet_name = wallet_name

        self.setObjectName("balanceTile")

        self.top_title = QLabel(self)
        self.top_title.setText("ACCOUNT BALANCE")
        self.top_title.setObjectName("balanceTileLabel")

        self.balance_label = QLabel(self)
        self.balance_label.setText(f"{format_balance(self.balance)} {self.currency.name}")
        self.top_title.setObjectName("balanceTileAmount")

        self.wallet_name_label = QLabel(self)
        self.wallet_name_label.setText(self.wallet_name)
        self.top_title.setObjectName("balanceTileWallet")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(self.top_title)
        main_layout.addWidget(self.balance_label)
        main_layout.addWidget(self.wallet_name_label)
        main_layout.addStretch()


    def set_data(self, balance:float = None, currency:Currency = None, wallet_name:str = None):
        """Set's data for widget"""
        if balance is not None:
            self.balance = balance

        if currency is not None:
            self.currency = currency

        if balance is not None or currency is not None:
            self._update_balance()

        if wallet_name is not None:
            self.wallet_name = wallet_name
            self._update_wallet()

    # Helpers
    def _update_balance(self):
        """Updates balance label"""
        self.balance_label.setText(f"{format_balance(self.balance)} {self.currency.name}")

    def _update_wallet(self):
        "Updates wallet name label"
        self.wallet_name_label.setText(self.wallet_name)





