from dataclasses import replace
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout
from ..service import WalletService
from app.database.models import Wallet
from enum import StrEnum
from app.core import (
    Frame,
    TextInput,
    PushButton,
    ComboBox,
    HLine,
    show_error,
)
from app.core.enums import Currency
from app.config import (
    WALLET_DIALOG_WIDTH,
    WALLET_DIALOG_HEIGHT,
)
from app.core.exceptions import AppError, ValidationError


class DialogType(StrEnum):
    CREATE = "CREATE"
    EDIT = "EDIT"


class WalletFormDialog(QDialog):
    """# Wallet Form Dialog

    Dialog used for creation of editing wallets.

    Wallet consist of:
    - Name
    - Currency
    - Initial balance
    """

    def __init__(self, service: WalletService, wallet: Wallet = None, parent=None):
        super().__init__(parent)

        self.service = service
        self.wallet = wallet
        self.dialog_type = DialogType.CREATE

        if self.wallet:
            self.dialog_type = DialogType.EDIT

        self.init_dialog()

    def init_dialog(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFixedWidth(WALLET_DIALOG_WIDTH)
        self.setFixedHeight(WALLET_DIALOG_HEIGHT)

        # Title
        self.title_label = QLabel(self)
        self.title_label.setText("New wallet" if not self.wallet else "Edit wallet")
        self.title_label.setObjectName("transactionLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        inputs_frame = Frame(self, add_stylesheet=False)
        input_layout = QVBoxLayout(inputs_frame)
        input_layout.setSpacing(0)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Transaction name input
        self.name_input = TextInput(
            parent=self,
            text="Name",
            placeholder="Enter wallet name",
            default_text=self._set_name(),
        )

        # Currency input
        self.currency_input = ComboBox(
            parent=self,
            text="Currency",
            placeholder="Choose currency",
            values=[
                (currency.value, "{0} - {1}".format(currency.name, currency.value))
                for currency in Currency
            ],
            default_value=self._set_currency(),
        )
        if self.dialog_type == DialogType.EDIT:
            self.currency_input.setEnabled(False)

        # Balance input
        self.in_balance_input = TextInput(
            parent=self,
            text="Initial Balance",
            placeholder="0,00",
            validate_number=True,
            default_text=self._set_initial_balance(),
        )

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.currency_input)
        input_layout.addWidget(self.in_balance_input)

        button_frame = Frame(self, add_stylesheet=False)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.hline = HLine()

        self.cancel_btn = PushButton(
            text="Cancel", alternate_look=True, on_click=self.close
        )

        self.create_btn = PushButton(
            text="Create" if self.dialog_type == DialogType.CREATE else "Save",
            on_click=self._create_or_save,
        )

        button_layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Add widgets
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(inputs_frame)
        main_layout.addStretch()
        main_layout.addWidget(self.hline)
        main_layout.addWidget(button_frame)

    # Setters for inputs
    def _set_name(self):
        """Set name for wallet input - if wallet provided"""
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return self.wallet.name
        return None

    def _set_currency(self):
        """Set currency for wallet - if wallet provided"""
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return "{0} - {1}".format(
                self.wallet.currency.name, self.wallet.currency.value
            )
        return None

    def _set_initial_balance(self):
        """Set initial balance for wallet - if wallet provided"""
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return f"{self.wallet.initial_balance:,.2f}".replace(",", " ").replace(
                ".", ","
            )
        return None

    def _create_or_save(self):
        """Create or save wallet in database"""
        # Validation
        msg = []

        # Validate inputs
        required_fields = {
            "name": self.name_input,
            "currency": self.currency_input,
            "initial balance": self.in_balance_input,
        }
        msg = [name for name, field in required_fields.items() if not field.is_filled()]

        # Display error box if sth must be filled
        if len(msg) > 0:
            self._show_error(f"Please fill in: {', '.join(msg)}")
            return

        if self.dialog_type == DialogType.EDIT:
            self._update_wallet()
        else:
            self._create_wallet()

    def _create_wallet(self):
        """Create wallet method"""
        try:
            self.service.create_wallet(
                user_id=self.service.app_state.active_user_id,
                name=self.name_input.get_value(),
                currency=self.currency_input.get_data(),
                initial_balance=self.in_balance_input.get_value(),
            )
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    def _update_wallet(self):
        """Update wallet method"""
        updated_wallet = replace(self.wallet)

        updated_wallet.name = self.name_input.get_value()
        updated_wallet.initial_balance = self.in_balance_input.get_value()

        try:
            self.service.update_wallet(wallet=updated_wallet)
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    def _show_error(self, msg: str):
        """Show error dialog"""
        show_error(self, message=msg)
