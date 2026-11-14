from dataclasses import replace
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from ..service import WalletService
from app.database.models import Wallet
from enum import StrEnum
from app.core import (
    Frame,
    TextInput,
    PushButton,
    ComboBox,
    HLine,
    SegmentedControl,
    show_error,
)
from app.core.utils import format_balance
from app.core.enums import Currency
from app.config import (
    WALLET_DIALOG_WIDTH,
    WALLET_DIALOG_HEIGHT,
)
from app.core.exceptions import AppError, ValidationError
from ..models import WalletSummary


class DialogType(StrEnum):
    CREATE = "CREATE"
    EDIT = "EDIT"


# Windows offered by the "Suggest from last N months" control.
SUGGESTION_WINDOWS = [(3, "3"), (6, "6"), (12, "12")]
DEFAULT_WINDOW = 6


class WalletFormDialog(QDialog):
    """# Wallet Form Dialog

    Dialog used for creation of editing wallets.

    Wallet consist of:
    - Name
    - Currency
    - Initial balance
    - Monthly plan (net salary, estimated expenses) used by the forecast
    """

    def __init__(self, service: WalletService, wallet: Wallet = None, parent=None):
        super().__init__(parent)

        self.service = service
        self.wallet = wallet
        self.dialog_type = DialogType.CREATE
        self.suggestion = None

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
            on_change=self._update_summary,
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

        # --- Monthly plan ------------------------------------------------
        self.month_control = SegmentedControl(
            text="Monthly plan",
            sub_text="Suggest from last",
            end_text="months",
            values=SUGGESTION_WINDOWS,
            default_value=DEFAULT_WINDOW,
            label_position="left",
            on_change=self._refresh_suggestions,
        )

        self.net_salary_edit = TextInput(
            self,
            text="Planned monthly income",
            sub_text="monthly",
            default_text=self._set_net_salary(),
            validate_number=True,
        )
        self.net_salary_edit.text_input.textEdited.connect(self._update_summary)

        self.income_hint, self.income_hint_label, self.income_hint_btn = (
            self._create_hint_row(on_use=self._use_income_suggestion)
        )

        self.basis_control = SegmentedControl(
            text="Planned expenses cover",
            # sub_text="Everything = expenses + savings + investments",
            values=[
                (0, "Expenses\nonly"),
                (1, "Expenses with savings\nand investmens"),
            ],
            default_value=1 if self._wallet_includes_transfers() else 0,
            label_position="left",
            on_change=self._basis_changed,
        )

        self.expenses_edit = TextInput(
            self,
            text="Estimated expenses",
            sub_text="monthly, used for forecasting. Excludes savings and investments.",
            default_text=self._set_planned_expenses(),
            validate_number=True,
        )
        self.expenses_edit.toggle_error(False)
        self.expenses_edit.text_input.textEdited.connect(self._update_summary)

        self.expenses_hint, self.expenses_hint_label, self.expenses_hint_btn = (
            self._create_hint_row(on_use=self._use_expense_suggestion)
        )

        summary_widget = QWidget(self)
        summary_widget.setObjectName("profileSummary")
        summary_layout = QHBoxLayout(summary_widget)
        summary_layout.setSpacing(5)
        summary_layout.setContentsMargins(10, 10, 10, 10)

        left_month_widget = QWidget(self)
        left_month_layout = QVBoxLayout(left_month_widget)
        left_month_layout.setSpacing(5)
        left_month_layout.setContentsMargins(0, 0, 0, 0)

        left_title = QLabel(self)
        left_title.setText("Left each month")
        left_title.setObjectName("leftMonthTitle")

        self.left_amount = QLabel(self)
        self.left_amount.setObjectName("leftMonthAmount")

        left_month_layout.addWidget(left_title)
        left_month_layout.addWidget(self.left_amount)

        savings_rate_widget = QWidget(self)
        savings_rate_layout = QVBoxLayout(savings_rate_widget)
        savings_rate_layout.setSpacing(5)
        savings_rate_layout.setContentsMargins(0, 0, 0, 0)

        savings_title = QLabel(self)
        savings_title.setText("Savings rate")
        savings_title.setObjectName("savingsRateLabel")

        self.savings_rate_amount = QLabel(self)
        self.savings_rate_amount.setObjectName("savingsRateAmount")

        savings_rate_layout.addWidget(savings_title)
        savings_rate_layout.addWidget(self.savings_rate_amount)

        summary_layout.addWidget(left_month_widget)
        summary_layout.addWidget(savings_rate_widget)

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.currency_input)
        input_layout.addWidget(self.in_balance_input)
        input_layout.addWidget(self.month_control)
        input_layout.addWidget(self.net_salary_edit)
        input_layout.addWidget(self.income_hint)
        input_layout.addWidget(self.basis_control)
        input_layout.addWidget(self.expenses_edit)
        input_layout.addWidget(self.expenses_hint)
        input_layout.addWidget(summary_widget)

        button_frame = Frame(self, add_stylesheet=False)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.hline = HLine()

        self.cancel_btn = PushButton(
            text="Cancel",
            object_name="dangerButton",
            width=80,
            height=30,
            on_click=self.close,
        )

        self.create_btn = PushButton(
            text="Create" if self.dialog_type == DialogType.CREATE else "Save",
            width=80,
            height=30,
            object_name="primaryButton",
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

        self._init_suggestions()
        self._update_summary()

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
            return self._format_amount(self.wallet.initial_balance)
        return None

    def _set_net_salary(self):
        """Set net salary for wallet - if wallet provided"""
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return self._format_amount(self.wallet.net_salary_monthly)
        return None

    def _set_planned_expenses(self):
        """Set estimated expenses for wallet - if wallet provided"""
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return self._format_amount(self.wallet.estimated_expenses_monthly)
        return None

    def _wallet_includes_transfers(self):
        if self.dialog_type == DialogType.EDIT and self.wallet is not None:
            return self.wallet.plan_includes_transfers
        return None

    @staticmethod
    def _format_amount(value):
        """Format a nullable amount for a text input. None stays empty."""
        if value is None:
            return None
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")

    def _currency_code(self):
        """Currency code for the summary - from the wallet, or the combo on create"""
        if self.wallet is not None:
            return self.wallet.currency.name
        data = self.currency_input.get_data()
        return Currency(data).name if data else ""

    def _basis_changed(self):
        if self.dialog_type == DialogType.CREATE or self.wallet is None:
            return

        # Refresh hint and hint label
        if self.wallet is not None:
            self._refresh_suggestions()

        # Refresh sub_text
        if bool(self.basis_control.get_data()):
            self.expenses_edit.set_sub_text(
                "monthly, used for forecasting. Includes savings and investments."
            )
        else:
            self.expenses_edit.set_sub_text(
                "monthly, used for forecasting. Excludes savings and investments."
            )

    # Suggestions
    def _create_hint_row(self, on_use):
        """Build a 'Last N months: X   Use' row that sits under an input."""
        widget = QWidget(self)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setSpacing(8)

        label = QLabel(widget)
        label.setObjectName("inputSubLabel")

        button = PushButton(
            text="Use",
            object_name="viewAllButton",
            width=34,
            height=18,
            on_click=on_use,
        )

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(button)

        widget.hide()
        return widget, label, button

    def _init_suggestions(self):
        """A new wallet has no history, so there is nothing to suggest from."""
        if self.dialog_type == DialogType.CREATE:
            self.month_control.hide()
            self.income_hint.hide()
            self.expenses_hint.hide()
            return

        months_available = self.service.get_months_of_history(
            wallet_id=self.wallet.id,
        )

        usable = [
            window for window, _ in SUGGESTION_WINDOWS if window <= months_available
        ]
        self.month_control.set_enabled_values(usable)

        if not usable:
            self.month_control.set_sub_text("Not enough history to suggest from")
            self.month_control.set_end_text("")
            return

        # Fall back to the widest window the wallet can actually cover.
        if self.month_control.get_data() not in usable:
            self.month_control.set_data(max(usable))

        self._refresh_suggestions()

    def _refresh_suggestions(self, months: int = None):
        """Recalculate both hints for the selected window."""
        if self.dialog_type == DialogType.CREATE or self.wallet is None:
            return

        if months is None:
            months = self.month_control.get_data()

        self.suggestion = self.service.get_plan_suggestion(
            wallet_id=self.wallet.id,
            months=months,
            include_transfers=bool(self.basis_control.get_data()),
        )

        if self.suggestion is None:
            self.income_hint.hide()
            self.expenses_hint.hide()
            return

        counted = self.suggestion.months_counted

        self.income_hint_label.setText(
            f"Last {counted} months: {format_balance(self.suggestion.income)}"
        )
        if bool(self.basis_control.get_data()):
            self.expenses_hint_label.setText(
                f"Last {counted} months, incl. transfers: "
                f"{format_balance(self.suggestion.expenses)}"
            )
        else:
            self.expenses_hint_label.setText(
                f"Last {counted} months, expenses only: "
                f"{format_balance(self.suggestion.expenses)}"
            )

        self.income_hint.show()
        self.expenses_hint.show()

    def _use_income_suggestion(self):
        """Copy the suggested income into the input"""
        if self.suggestion is None:
            return
        self.net_salary_edit.set_value(self._format_amount(self.suggestion.income))
        self._update_summary()

    def _use_expense_suggestion(self):
        """Copy the suggested expenses into the input"""
        if self.suggestion is None:
            return
        self.expenses_edit.set_value(self._format_amount(self.suggestion.expenses))
        self._update_summary()

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
                net_salary_monthly=self._plan_value(self.net_salary_edit),
                estimated_expenses_monthly=self._plan_value(self.expenses_edit),
                plan_includes_transfers=self.basis_control.get_data(),
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
        updated_wallet.net_salary_monthly = self._plan_value(self.net_salary_edit)
        updated_wallet.estimated_expenses_monthly = self._plan_value(self.expenses_edit)
        updated_wallet.plan_includes_transfers = self.basis_control.get_data()

        try:
            self.service.update_wallet(wallet=updated_wallet)
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    @staticmethod
    def _plan_value(field):
        """Empty plan field means 'not set' (NULL), not zero."""
        if not field.is_filled():
            return None
        return field.get_value()

    def _show_error(self, msg: str):
        """Show error dialog"""
        show_error(self, message=msg)

    def _update_summary(self):
        """Updates summary widget - live recompute"""

        net = self._plan_value(self.net_salary_edit)
        expenses = self._plan_value(self.expenses_edit)

        self.wallet_summary = self.service.calculate_summary(
            net=net,
            expenses=expenses,
        )

        sign = "+" if self.wallet_summary.left_each_month >= 0 else "-"
        self.left_amount.setText(
            f"{sign}{format_balance(abs(self.wallet_summary.left_each_month))} "
            f"{self._currency_code()}"
        )

        self.savings_rate_amount.setText(
            f"{format_balance(self.wallet_summary.savings_rate * 100)}%"
            if self.wallet_summary.savings_rate is not None
            else "-"
        )

        positive = "true" if self.wallet_summary.left_each_month >= 0 else "false"
        for label in (self.left_amount, self.savings_rate_amount):
            label.setProperty("positive", positive)
            label.style().unpolish(label)
            label.style().polish(label)
