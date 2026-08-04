from dataclasses import replace
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QScrollArea,
    QDialog,
)

from app.core import (
    Frame,
    TextInput,
    PushButton,
    ComboBox,
    DateInput,
    HLine,
    show_error,
    cast_datetime_to_str
)

from app.core.enums import OperationType, RecurrenceInterval
from .service import TransactionService
from app.config import (
    TRANSACTION_WINDOW_WIDTH,
    TRANSACTION_WINDOW_HEIGHT,
)
from app.core.exceptions import ValidationError, AppError
from app.database.models import Transaction, RecurringTransaction
from enum import StrEnum


class CREATION_TYPE(StrEnum):
    CREATE = "create"
    EDIT_RECURRING = "edit-recurring"
    EDIT_ONE_TIME = "edit_one_time"


class TransactionView(QDialog):
    def __init__(
        self,
        service: TransactionService,
        transaction: Transaction | RecurringTransaction = None,
        parent=None,
    ):
        super().__init__(parent)

        self.service = service
        self.transaction = transaction

        self.main_categories = self.service.get_all_main_categories(
            wallet_id=self.service.get_active_wallet().id
        )

        self.sub_categories = self.service.get_all_sub_categories(
            self.main_categories[0].name
        )

        if transaction is None:
            self._mode = CREATION_TYPE.CREATE
        elif isinstance(transaction, RecurringTransaction):
            self._mode = CREATION_TYPE.EDIT_RECURRING
        else:
            self._mode = CREATION_TYPE.EDIT_ONE_TIME

        self._init_view()

    def _init_view(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFixedWidth(TRANSACTION_WINDOW_WIDTH)
        self.setFixedHeight(TRANSACTION_WINDOW_HEIGHT)

        # Scroll Area dla widżetu
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Główny layout contentu
        self.content = QWidget()
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(5, 10, 5, 10)
        self.content_layout.setSpacing(5)

        self.scroll_area.setWidget(self.content)

        # Title
        self.title_label = QLabel(self)
        self.title_label.setText(
            "New transaction" if self.transaction is None else "Edit transaction"
        )
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
            placeholder="Enter transaction name",
            default_text=self._set_title(),
        )

        # Description input
        self.description_input = TextInput(
            parent=self,
            text="Description",
            placeholder="Enter description (optional)",
            is_multiline=True,
            default_text=self._set_description(),
        )

        # Payee input
        self.payee_input = TextInput(
            parent=self,
            text="Payee",
            placeholder="Enter payee",
            default_text=self._set_payee(),
        )

        wallet_type_frame = Frame(self, add_stylesheet=False)
        wallet_type_layout = QHBoxLayout(wallet_type_frame)
        wallet_type_layout.setContentsMargins(0, 0, 0, 0)
        wallet_type_layout.setSpacing(10)

        self.wallet_input = ComboBox(
            parent=self,
            text="Wallet",
            placeholder="Choose wallet",
            values=[
                (wallet.id, wallet.name) for wallet in self.service.get_all_wallets()
            ],
            default_value=self._set_wallet(),
            on_change=self._on_wallet_change,
        )

        self.operation_type_input = ComboBox(
            parent=self,
            text="Type",
            placeholder="Choose type",
            values=[(type.value, type.value) for type in OperationType],
            default_value=self._set_operation_type(),
        )

        wallet_type_layout.addWidget(self.wallet_input)
        wallet_type_layout.addWidget(self.operation_type_input)

        category_frame = Frame(self, add_stylesheet=False)
        category_layout = QHBoxLayout(category_frame)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(10)

        self.main_category_input = ComboBox(
            parent=self,
            text="Main Category",
            placeholder="Choose category",
            values=[(category.id, category.name) for category in self.main_categories],
            default_value=self._set_main_category(),
            on_change=self._on_main_category_change,
        )

        self.sub_category_input = ComboBox(
            parent=self,
            text="Subcategory",
            placeholder="Choose category",
            values=[(category.id, category.name) for category in self.sub_categories],
            default_value=self._set_sub_category(),
        )

        category_layout.addWidget(self.main_category_input)
        category_layout.addWidget(self.sub_category_input)

        # Amount input
        self.amount_input = TextInput(
            parent=self,
            text="Amount",
            placeholder="0,00",
            validate_number=True,
            default_text=self._set_amount(),
        )

        date_frame = Frame(self, add_stylesheet=False)
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(10)

        self.start_date_input = DateInput(
            parent=self,
            text="Start date",
            on_date_change=self._on_start_date_change,
            default_date=self._set_date(),
        )

        self.transaction_repeat_input = ComboBox(
            parent=self,
            text="Repetition",
            placeholder="Choose repeat interval",
            values=[(type.index, type.value) for type in RecurrenceInterval],
            default_value=self._set_interval(),
            on_change=self._on_repeat_change,
        )

        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(self.transaction_repeat_input)

        self.end_date_input = DateInput(
            parent=self,
            text="End date (optional, leave empty for until cancelled)",
            on_date_change=self._on_end_date_change,
            nullable=True,
            placeholder="Select date",
            default_date=self._set_end_date(),
        )

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(
            self.description_input, alignment=Qt.AlignmentFlag.AlignTop
        )
        input_layout.addWidget(self.payee_input)
        input_layout.addWidget(wallet_type_frame)
        input_layout.addWidget(category_frame)
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(date_frame)
        input_layout.addWidget(self.end_date_input)

        button_frame = Frame(self, add_stylesheet=False)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.hline = HLine()

        self.cancel_btn = PushButton(
            text="Cancel", alternate_look=True, on_click=self.close
        )

        self.create_btn = PushButton(
            text="Create" if self._mode == CREATION_TYPE.CREATE else "Save",
        )

        button_layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.content_layout.addWidget(self.title_label)
        self.content_layout.addWidget(inputs_frame)
        self.content_layout.addStretch()
        self.content_layout.addWidget(self.hline)
        self.content_layout.addWidget(button_frame)

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(
            self.scroll_area,
        )

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        match self._mode:
            case CREATION_TYPE.CREATE:
                self.create_btn.set_on_click(on_click=self._create_transaction)
            case CREATION_TYPE.EDIT_RECURRING:
                self.transaction_repeat_input.show()
                self.end_date_input.show()
                self.create_btn.set_on_click(
                    on_click=self._update_recurring_transaction
                )
            case CREATION_TYPE.EDIT_ONE_TIME:
                self.transaction_repeat_input.hide()
                self.end_date_input.hide()
                self.start_date_input.set_label_text(text="Date")
                self.create_btn.set_on_click(on_click=self._update_transaction)

        self._on_repeat_change()

    def _set_title(self) -> str:
        return self.transaction.title if self.transaction is not None else None

    def _set_description(self) -> str:
        return self.transaction.description if self.transaction is not None else None

    def _set_payee(self) -> str:
        return self.transaction.merchant if self.transaction is not None else None

    def _set_wallet(self) -> str:
        return (
            self.service.get_wallet_by_id(id=self.transaction.wallet_id).name
            if self.transaction is not None
            else self.service.get_active_wallet().name
        )

    def _set_operation_type(self) -> str:
        return (
            self.transaction.operation_type
            if self.transaction is not None
            else OperationType.EXPENSE.value
        )

    def _set_main_category(self) -> str:
        if self.transaction is not None:
            main_cat = self.service.get_main_category_by_id(
                sub_id=self.transaction.category_id
            )

            self.sub_categories = self.service.get_all_sub_categories(main_cat.name)

            return main_cat.name

        return self.main_categories[0].name

    def _set_sub_category(self) -> str:
        if self.transaction is not None:

            sub_cat = self.service.get_sub_category_by_id(
                id=self.transaction.category_id
            )

            return sub_cat.name

        return self.sub_categories[0].name

    def _set_amount(self):
        return (
            f"{self.transaction.amount:,.2f}".replace(",", " ").replace(".", ",")
            if self.transaction is not None
            else None
        )

    def _set_date(self):
        if self.transaction is None:
            return None
        if self._mode == CREATION_TYPE.EDIT_RECURRING:
            return self.transaction.start_date
        return self.transaction.date

    def _set_interval(self):
        if self._mode == CREATION_TYPE.EDIT_RECURRING:
            return self.transaction.recurrence_interval

        return RecurrenceInterval.DOES_NOT_REPEAT.value

    def _set_end_date(self):
        if self._mode == CREATION_TYPE.EDIT_RECURRING:
            return self.transaction.end_date

        return None

    def _on_repeat_change(self):
        """On repeat change trigger - show/hide end date box"""
        current_repeat = RecurrenceInterval(self.transaction_repeat_input.get_value())

        if current_repeat == RecurrenceInterval.DOES_NOT_REPEAT:
            self.end_date_input.setVisible(False)
        else:
            self.end_date_input.setVisible(True)

    def _on_main_category_change(self):
        """On main category change trigger - updates sub categories list"""
        current_category = self.main_category_input.get_value()

        wallet_id = self.wallet_input.get_data()
        wallet = self.service.get_wallet_by_id(wallet_id)

        self.sub_categories = self.service.get_all_sub_categories(
            name=current_category, wallet_id=wallet.id
        )

        self.sub_category_input.add_items_with_data(
            items=[(category.id, category.name) for category in self.sub_categories]
        )

    def _on_start_date_change(self):
        """On start data chnage trigger - sets start date to be higher or be todays date if any interval was choosen"""
        start_date = self.start_date_input.get_value()
        interval = RecurrenceInterval(self.transaction_repeat_input.get_value())

        proper_date = self.service.validate_start_date(
            start_date=start_date, interval=interval
        )

        if proper_date is not None:
            self.start_date_input.set_date(proper_date)

        self._on_end_date_change()

    def _on_end_date_change(self):
        """On end data chnage trigger - sets end date to be higher or equal start date"""
        start_date = self.start_date_input.get_value()
        end_date = self.end_date_input.get_value()

        if end_date is not None:

            proper_date = self.service.validate_end_date(
                start_date=start_date, end_date=end_date
            )

            if proper_date is not None:
                self.end_date_input.set_date(proper_date)

    def _on_wallet_change(self):
        """On wallet change trigger - updates list of categories"""
        wallet_id = self.wallet_input.get_data()
        wallet = self.service.get_wallet_by_id(wallet_id)

        self.main_categories = self.service.get_all_main_categories(wallet_id=wallet.id)

        self.sub_categories = self.service.get_all_sub_categories(
            name=self.main_categories[0].name, wallet_id=wallet.id
        )

        self.main_category_input.update_items(
            items=[category.name for category in self.main_categories]
        )
        self.sub_category_input.update_items(
            items=[category.name for category in self.sub_categories]
        )

    def _show_error(self, msg: str):
        """Show error dialog"""
        show_error(self, message=msg)

    def _validate_inputs(self) -> bool:
        msg = []

        # Validate inputs
        required_fields = {
            "name": self.name_input,
            "date": self.start_date_input,
            "wallet": self.wallet_input,
            "operation type": self.operation_type_input,
            "main category": self.main_category_input,
            "sub category": self.sub_category_input,
            "amount": self.amount_input,
        }
        msg = [name for name, field in required_fields.items() if not field.is_filled()]

        # Display error box if sth must be filled
        if len(msg) > 0:
            self._show_error(f"Please fill in: {', '.join(msg)}")
            return False

        return True

    def _create_transaction(self):
        """Create transaction and/or recurring transaction - based on user choices."""
        if not self._validate_inputs():
            return

        wallet_id = self.wallet_input.get_data()
        wallet = self.service.get_wallet_by_id(wallet_id)

        try:
            self.service.create_transaction(
                wallet=wallet,
                category_name=self.sub_category_input.get_value(),
                title=self.name_input.get_value(),
                start_date=self.start_date_input.get_value(),
                operation_type=OperationType(self.operation_type_input.get_data()),
                amount=self.amount_input.get_value(),
                description=self.description_input.get_value(),
                merchant=self.payee_input.get_value(),
                repeat_interval=RecurrenceInterval(
                    self.transaction_repeat_input.get_value()
                ),
                end_date=self.end_date_input.get_value(),
            )
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    def _update_transaction(self):
        if not self._validate_inputs():
            return

        updated_transaction = replace(self.transaction)

        updated_transaction.title = self.name_input.get_value()
        updated_transaction.description = self.description_input.get_value()
        updated_transaction.merchant = self.payee_input.get_value()
        updated_transaction.wallet_id = self.wallet_input.get_data()
        updated_transaction.operation_type = OperationType(
            self.operation_type_input.get_data()
        )
        updated_transaction.category_id = self.sub_category_input.get_data()
        updated_transaction.amount = self.amount_input.get_value()
        updated_transaction.date = self.start_date_input.get_value()

        try:
            self.service.update_transaction(transaction=updated_transaction)
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    def _update_recurring_transaction(self):
        if not self._validate_inputs():
            return

        updated_transaction = replace(self.transaction)

        updated_transaction.title = self.name_input.get_value()
        updated_transaction.description = self.description_input.get_value()
        updated_transaction.merchant = self.payee_input.get_value()
        updated_transaction.wallet_id = self.wallet_input.get_data()
        updated_transaction.operation_type = OperationType(
            self.operation_type_input.get_data()
        )
        updated_transaction.category_id = self.sub_category_input.get_data()
        updated_transaction.amount = self.amount_input.get_value()
        updated_transaction.start_date = self.start_date_input.get_value()
        updated_transaction.end_date = self.end_date_input.get_value()
        updated_transaction.recurrence_interval = RecurrenceInterval(
            self.transaction_repeat_input.get_value()
        )

        try:
            self.service.update_recurring_transaction(transaction=updated_transaction)
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")
