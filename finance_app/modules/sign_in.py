from PySide6.QtCore import *
from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget

import json

from finance_app import center_window
from finance_app.config import *


class SignInWindow(QWidget):
    """
    Sign in window where user provides information listed below:
        - Name
        - Current account balance
        - Monthly gross salary
        - Monthly net salary
        - Average monthly expenses
        - Curency to display
        - Path to folder with data

    Sign in window is triggered when no user data where found.

    """

    signed_in_signal = Signal(bool)

    def __init__(self, user_settings, user_setings_path) -> None:
        super().__init__()

        # User information
        self.user_name = None
        self.current_acc_balance = None
        self.monthly_gross_salary = None
        self.monthly_net_salary = None
        self.avg_monthly_expense = None
        self.currency = None
        self.data_path = None

        # User setting
        self.user_settings = user_settings
        self.user_setings_path = user_setings_path

        # Value validator
        self.double_validator = QDoubleValidator()
        self.double_validator.setDecimals(2)

        self.init_window()

    def init_window(self):
        """
        Initialize sign in window
        """
        self.setWindowTitle("Finance App")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Title layout
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # App logo
        self.logo_pimap = QPixmap(LOGO_PATH)
        self.logo_pimap = self.logo_pimap.scaledToHeight(50)
        self.logo_pimap = self.logo_pimap.scaledToWidth(50)
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(self.logo_pimap)

        # Title box'a
        self.title_label = QLabel(self)
        self.title_label.setText("Finance App")
        self.title_label.setContentsMargins(0, 0, 15, 0)
        self.title_label.setStyleSheet("color: black; font-size: 18pt;")

        title_layout.addWidget(
            self.logo_label, 0, alignment=Qt.AlignmentFlag.AlignRight
        )
        title_layout.addWidget(
            self.title_label, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Credential layout
        cred_layout = QGridLayout()
        cred_layout.setSpacing(12)

        # Name label
        self.name_label = QLabel(self)
        self.name_label.setText("Name")
        self.name_label.setContentsMargins(15, 0, 15, 0)
        self.name_label.setStyleSheet("color: black; font-size: 10pt;")

        # Name entry
        self.name_entry = QLineEdit(self)
        self.name_entry.setStyleSheet("padding: 5px;")

        # Current account balance label
        self.acc_bal_label = QLabel(self)
        self.acc_bal_label.setText("Current account balance")
        self.acc_bal_label.setContentsMargins(15, 0, 15, 0)
        self.acc_bal_label.setStyleSheet("color: black; font-size: 10pt;")

        # Current account balance entry
        self.acc_bal_entry = QLineEdit(self)
        self.acc_bal_entry.setStyleSheet("padding: 5px;")
        self.acc_bal_entry.setValidator(self.double_validator)

        # Monthly gross salary label
        self.gross_salary_label = QLabel(self)
        self.gross_salary_label.setText("Monthly gross salary")
        self.gross_salary_label.setContentsMargins(15, 0, 15, 0)
        self.gross_salary_label.setStyleSheet("color: black; font-size: 10pt;")

        # Monthly gross salary  entry
        self.gross_salary_entry = QLineEdit(self)
        self.gross_salary_entry.setStyleSheet("padding: 5px;")
        self.gross_salary_entry.setValidator(self.double_validator)

        # Monthly net salary label
        self.net_salary_label = QLabel(self)
        self.net_salary_label.setText("Monthly net salary")
        self.net_salary_label.setContentsMargins(15, 0, 15, 0)
        self.net_salary_label.setStyleSheet("color: black; font-size: 10pt;")

        # Monthly net salary  entry
        self.net_salary_entry = QLineEdit(self)
        self.net_salary_entry.setStyleSheet("padding: 5px;")
        self.net_salary_entry.setValidator(self.double_validator)

        # Average monthly expenses label
        self.avg_expenses_label = QLabel(self)
        self.avg_expenses_label.setText("Average monthly expenses")
        self.avg_expenses_label.setContentsMargins(15, 0, 15, 0)
        self.avg_expenses_label.setStyleSheet("color: black; font-size: 10pt;")

        # Average monthly expenses entry
        self.avg_expenses_entry = QLineEdit(self)
        self.avg_expenses_entry.setStyleSheet("padding: 5px;")
        self.avg_expenses_entry.setValidator(self.double_validator)

        # Currency label
        self.currency_label = QLabel(self)
        self.currency_label.setText("Currency")
        self.currency_label.setContentsMargins(15, 0, 15, 0)
        self.currency_label.setStyleSheet("color: black; font-size: 10pt;")

        # Currency entry
        self.currency_entry = QComboBox(self)
        self.currency_entry.setStyleSheet("padding: 5px;")
        self.currency_entry.addItems(CURRENCIES.keys())
        self.currency_entry.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # User setting folder label
        self.data_dir_label = QLabel(self)
        self.data_dir_label.setText("Data folder")
        self.data_dir_label.setContentsMargins(15, 0, 15, 0)
        self.data_dir_label.setStyleSheet("color: black; font-size: 10pt;")

        # Data dir layout
        data_dir_widget = QWidget()
        data_dir_layout = QHBoxLayout(data_dir_widget)
        data_dir_layout.setContentsMargins(0, 0, 0, 0)
        data_dir_layout.setSpacing(0)

        # User setting folder entry
        self.data_dir_entry = QLineEdit(self)
        self.data_dir_entry.setMinimumHeight(37)
        self.data_dir_entry.setStyleSheet(
            "border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
        )
        self.data_dir_entry.setPlaceholderText("Choose folder")

        self.folder_browser_btn = QPushButton()
        self.folder_browser_btn.setText("Browse")
        self.folder_browser_btn.setStyleSheet(
            "QPushButton {background-color: #97a7b4; border-style: solid; border-color: #97a7b4; border-width: 2px; border-radius: 10px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; font-size: 10pt; font-weight:bold;} "
            + "QPushButton::pressed {background-color: #b5c0c9; border-style: solid; border-color: #b5c0c9; border-width: 2px; border-radius: 10px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; font-size: 10pt; font-weight:bold;}"
        )
        self.folder_browser_btn.setMinimumHeight(37)
        self.folder_browser_btn.setMinimumWidth(80)
        self.folder_browser_btn.clicked.connect(self.choose_save_folder)

        data_dir_layout.addWidget(self.data_dir_entry)
        data_dir_layout.addWidget(self.folder_browser_btn)

        # Create account button
        self.create_acc_btn = QPushButton(self)
        self.create_acc_btn.setText("Create account")
        self.create_acc_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; font-weight:bold;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; font-weight:bold;}"
        )
        self.create_acc_btn.setMinimumHeight(45)
        self.create_acc_btn.setMinimumWidth(150)
        self.create_acc_btn.clicked.connect(self.create_account)

        # Adding widgets to layout
        cred_layout.addWidget(
            self.name_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.name_entry, 0, 1)
        cred_layout.addWidget(
            self.acc_bal_label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.acc_bal_entry, 1, 1)
        cred_layout.addWidget(
            self.gross_salary_label, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.gross_salary_entry, 2, 1)
        cred_layout.addWidget(
            self.net_salary_label, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.net_salary_entry, 3, 1)
        cred_layout.addWidget(
            self.avg_expenses_label, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.avg_expenses_entry, 4, 1)
        cred_layout.addWidget(
            self.currency_label, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(self.currency_entry, 5, 1)
        cred_layout.addWidget(
            self.data_dir_label, 6, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        cred_layout.addWidget(data_dir_widget, 6, 1)
        cred_layout.addWidget(
            self.create_acc_btn, 7, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Spacer for bottom
        self.spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addLayout(title_layout, 0)
        main_layout.addLayout(cred_layout, 0)
        main_layout.addItem(self.spacer)

    def choose_save_folder(self):
        """
        Method used for selecting user data folder.
        """
        # Filedialog to folder path to choose
        data_path = QFileDialog.getExistingDirectory(
            self,
            caption="Choose data folder",
            options=QFileDialog.ShowDirsOnly,
        )

        # Update user data path entry if any dir has been choosen
        if data_path != "":
            self.data_path = data_path
            self.data_dir_entry.setText(self.data_path)

    def create_account(self):
        """
        Method user for creating user account based on information provided by the user.
        User data is saved in settings path based on platformdirs library.
        """
        # Get user values
        self.user_name = self.name_entry.text()
        self.current_acc_balance = float(self.acc_bal_entry.text().replace(",", "."))
        self.monthly_gross_salary = float(
            self.gross_salary_entry.text().replace(",", ".")
        )
        self.monthly_net_salary = float(self.net_salary_entry.text().replace(",", "."))
        self.avg_monthly_expense = float(
            self.avg_expenses_entry.text().replace(",", ".")
        )
        self.currency = self.currency_entry.currentText()

        # Dict with info
        user_settings_dict = {
            "USER_NAME": self.user_name,
            "CURRENT_ACCOUNT_BALANCE": self.current_acc_balance,
            "MONTHLY_GROSS_SALARY": self.monthly_gross_salary,
            "MONTHLY_NET_SALARY": self.monthly_net_salary,
            "AVERAGE_MONTHLY_EXPENSE": self.avg_monthly_expense,
            "CURRENCY": self.currency,
            "USER_FOLDER": self.data_path,
            "DEFAULT_VIEW": "Home",
        }

        # Save user information to settings folder
        with open(self.user_setings_path, "w") as file:
            json.dump(user_settings_dict, file)

        self.signed_in_signal.emit(True)
        self.destroy()
