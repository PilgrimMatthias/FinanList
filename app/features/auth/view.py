from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QStackedWidget,
    QGridLayout,
    QSpacerItem,
)
from app.core import (
    Frame,
    LogoWidget,
    TextInput,
    PushButton,
    ComboBox,
    UserProfileWidget,
)
from app.core.enums import Currency
from .service import AuthService
from app.config import APP_NAME, APP_LOGO_SVG


class AuthView(QWidget):
    def __init__(self, service: AuthService):
        super().__init__()

        self.service = service

        self._init_view()

    def _init_view(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        # Logo
        logo_frame = Frame(self, add_stylesheet=False)

        self.logo_layout = QHBoxLayout(logo_frame)
        self.logo_layout.setSpacing(10)

        self.logo_icon = LogoWidget(self, file=str(APP_LOGO_SVG))
        self.logo_icon.setFixedSize(60, 60)

        self.logo_label = QLabel(self, text=APP_NAME)
        self.logo_label.setObjectName("logoLabel")

        self.logo_layout.addWidget(
            self.logo_icon, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.logo_layout.addWidget(
            self.logo_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        user_list_frame = self._create_user_list_widget()

        sign_up_frame = self._create_sign_up_widget()

        self.stack_widget = QStackedWidget(self)
        self.stack_widget.addWidget(user_list_frame)
        self.stack_widget.addWidget(sign_up_frame)

        self.stack_widget.setCurrentIndex(0)

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(logo_frame)
        main_layout.addWidget(self.stack_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    def _create_user_list_widget(self) -> Frame:
        """Create user list widget"""
        user_list_frame = Frame(self, add_stylesheet=False)

        user_list_layout = QGridLayout(user_list_frame)

        col_counter = 0
        row_counter = 0
        for user in self.service.get_all_users():

            temp_user_widget = UserProfileWidget(
                self,
                initial=user.name[0],
                username=user.name,
                on_click=lambda uid=user.id: self.service.select_user(uid),
            )

            user_list_layout.addWidget(temp_user_widget, row_counter, col_counter)

            col_counter += 1

            if col_counter == 3:
                col_counter = 0
                row_counter += 1

        user_list_layout.setColumnStretch(0, 0)
        user_list_layout.setColumnStretch(1, 0)
        user_list_layout.setColumnStretch(2, 0)

        new_user_widget = UserProfileWidget(
            self,
            initial="+",
            username="Create New\nUser",
            on_click=lambda: self.stack_widget.setCurrentIndex(1),
        )

        user_list_layout.addWidget(new_user_widget, row_counter, col_counter + 1)

        return user_list_frame

    def _create_sign_up_widget(self) -> Frame:
        """Create sign up widget box"""
        sign_up_widget = Frame(self)

        sign_up_layout = QVBoxLayout(sign_up_widget)
        sign_up_layout.setSpacing(0)

        self.name_input = TextInput(self, text="Name", placeholder="Enter your name")
        self.gross_salary_input = TextInput(
            self,
            text="Gross salary (monthly)",
            placeholder="Enter your monthly gross salary",
            validate_number=True,
        )
        self.net_salary_input = TextInput(
            self,
            text="Net salary (monthly)",
            placeholder="Enter your monthly net salary",
            validate_number=True,
        )
        self.avg_expenses_input = TextInput(
            self,
            text="Average expenses (monthly)",
            placeholder="Enter your monthly average expenses",
            validate_number=True,
        )
        self.initial_balance_input = TextInput(
            self,
            text="Current account balance",
            placeholder="Enter your current account balance",
            validate_number=True,
        )
        self.currency_input = ComboBox(
            self,
            text="Currency",
            placeholder="Choose your preffered currency",
            values=[
                "{0} - {1}".format(currency.name, currency.value)
                for currency in Currency
            ],
            default_value="{0} - {1}".format(Currency.PLN.name, Currency.PLN.value),
        )

        # Navigation frame and layout
        navigation_btn_frame = QWidget(self)
        self.navigation_layout = QHBoxLayout(navigation_btn_frame)

        self.signup_btn = PushButton(text="Sign Up", on_click=self._on_sign_up)
        self.cancel_btn = PushButton(
            text="Cancel",
            alternate_look=True,
            on_click=self._on_cancel,
        )

        self.navigation_layout.addStretch()
        self.navigation_layout.addWidget(
            self.cancel_btn, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.navigation_layout.addWidget(
            self.signup_btn,
        )
        self.navigation_layout.setContentsMargins(0, 0, 0, 0)

        sign_up_layout.addWidget(self.name_input)
        sign_up_layout.addWidget(self.gross_salary_input)
        sign_up_layout.addWidget(self.net_salary_input)
        sign_up_layout.addWidget(self.avg_expenses_input)
        sign_up_layout.addWidget(self.initial_balance_input)
        sign_up_layout.addWidget(self.currency_input)
        sign_up_layout.addWidget(navigation_btn_frame)
        sign_up_layout.addStretch()

        return sign_up_widget

    def _on_sign_up(self):
        """
        On sign up manages validation of user inputs, creating user and refreshing UI.
        """
        msg = []

        # Validate inputs
        required_fields = {
            "name": self.name_input,
            "gross salary": self.gross_salary_input,
            "net salary": self.net_salary_input,
            "average expenses": self.avg_expenses_input,
            "initial balance": self.initial_balance_input,
        }
        msg = [name for name, field in required_fields.items() if not field.is_filled()]

        # Display error box if sth must be filled
        if len(msg) > 0:
            print("Error box should fire")
            print(msg)
            return

        self.service.create_user(
            name=self.name_input.get_value(),
            gross_salary_monthly=self.gross_salary_input.get_value(),
            net_salary_monthly=self.net_salary_input.get_value(),
            estimated_expenses_monthly=self.avg_expenses_input.get_value(),
            initial_balance=self.initial_balance_input.get_value(),
            currency=self._parse_currency(),
        )

        self._clear_sign_up_form()
        self._refresh_user_list()
        self.stack_widget.setCurrentIndex(0)

    def _parse_currency(self) -> Currency:
        """Currency parser based on currency input"""
        currency_value = self.currency_input.get_value().split(" - ")[1]
        return Currency(currency_value)

    def _refresh_user_list(self):
        """Refresh user list widget with list of all users. Updates everytime user is created"""
        old_widget = self.stack_widget.widget(0)
        new_widget = self._create_user_list_widget()
        self.stack_widget.removeWidget(old_widget)
        old_widget.deleteLater()
        self.stack_widget.insertWidget(0, new_widget)

    def _clear_sign_up_form(self):
        """Clear sign up form after _on_signup"""
        self.name_input.clear()
        self.gross_salary_input.clear()
        self.net_salary_input.clear()
        self.avg_expenses_input.clear()
        self.initial_balance_input.clear()

    def _on_cancel(self):
        """Cancel form and return to user screen"""
        self._clear_sign_up_form()
        self.stack_widget.setCurrentIndex(0)
