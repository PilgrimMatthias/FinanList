from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime
from platformdirs import user_data_dir

from finance_app.config import *


class AccountSettings(QWidget):
    """
    Account settings window
    """

    # Signals
    update_settings = Signal()
    account_deletion = Signal()

    def __init__(self, parent, user_settings, user_settings_path):
        super().__init__()

        # User data
        self.user_settings = user_settings
        self.user_settings_path = user_settings_path

        self.username = self.user_settings.get("USER_NAME")
        self.acc_balance = str(self.user_settings.get("CURRENT_ACCOUNT_BALANCE"))
        self.gross_salary = str(self.user_settings.get("MONTHLY_GROSS_SALARY"))
        self.net_salary = str(self.user_settings.get("MONTHLY_NET_SALARY"))
        self.avg_expenses = str(self.user_settings.get("AVERAGE_MONTHLY_EXPENSE"))
        self.currency = self.user_settings.get("CURRENCY")
        self.user_folder = self.user_settings.get("USER_FOLDER")

        # Variables
        self.validator = QDoubleValidator(bottom=0, decimals=2)
        self.validator.setNotation(QDoubleValidator.StandardNotation)

        self.today = datetime.today()
        self.active = False

        self.init_ui()

    def init_ui(self):
        """
        Initialization of accounts settings window
        """
        self.setWindowTitle("Account Settings")

        main_layout = QGridLayout()
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(QSize(550, 375))
        self.setFixedSize(QSize(500, 450))
        self.setLayout(main_layout)
        main_layout.setSpacing(10)

        # Name label
        self.name_label = QLabel(self)
        self.name_label.setText("Name")
        self.name_label.setContentsMargins(15, 0, 15, 0)
        self.name_label.setStyleSheet("color: black; font-size: 10pt;")

        # Name entry
        self.name_entry = QLineEdit(self)
        self.name_entry.setStyleSheet("padding: 5px;")
        self.name_entry.setText(self.username)
        self.name_entry.setEnabled(False)

        # Current account balance label
        self.acc_bal_label = QLabel(self)
        self.acc_bal_label.setText("Current account balance")
        self.acc_bal_label.setContentsMargins(15, 0, 15, 0)
        self.acc_bal_label.setStyleSheet("color: black; font-size: 10pt;")

        # Current account balance entry
        self.acc_bal_entry = QLineEdit(self)
        self.acc_bal_entry.setStyleSheet("padding: 5px;")
        self.acc_bal_entry.setValidator(self.validator)
        self.acc_bal_entry.setText(self.acc_balance)
        self.acc_bal_entry.setEnabled(False)

        # Monthly gross salary label
        self.gross_salary_label = QLabel(self)
        self.gross_salary_label.setText("Monthly gross salary")
        self.gross_salary_label.setContentsMargins(15, 0, 15, 0)
        self.gross_salary_label.setStyleSheet("color: black; font-size: 10pt;")

        # Monthly gross salary  entry
        self.gross_salary_entry = QLineEdit(self)
        self.gross_salary_entry.setStyleSheet("padding: 5px;")
        self.gross_salary_entry.setValidator(self.validator)
        self.gross_salary_entry.setText(self.gross_salary)
        self.gross_salary_entry.setEnabled(False)

        # Monthly net salary label
        self.net_salary_label = QLabel(self)
        self.net_salary_label.setText("Monthly net salary")
        self.net_salary_label.setContentsMargins(15, 0, 15, 0)
        self.net_salary_label.setStyleSheet("color: black; font-size: 10pt;")

        # Monthly net salary  entry
        self.net_salary_entry = QLineEdit(self)
        self.net_salary_entry.setStyleSheet("padding: 5px;")
        self.net_salary_entry.setValidator(self.validator)
        self.net_salary_entry.setText(self.net_salary)
        self.net_salary_entry.setEnabled(False)

        # Average monthly expenses label
        self.avg_expenses_label = QLabel(self)
        self.avg_expenses_label.setText("Average monthly expenses")
        self.avg_expenses_label.setContentsMargins(15, 0, 15, 0)
        self.avg_expenses_label.setStyleSheet("color: black; font-size: 10pt;")

        # Average monthly expenses entry
        self.avg_expenses_entry = QLineEdit(self)
        self.avg_expenses_entry.setStyleSheet("padding: 5px;")
        self.avg_expenses_entry.setValidator(self.validator)
        self.avg_expenses_entry.setText(self.avg_expenses)
        self.avg_expenses_entry.setEnabled(False)

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
        self.currency_entry.setCurrentText(self.currency)
        self.currency_entry.setEnabled(False)

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
        # self.data_dir_entry.setMinimumWidth(140)
        self.data_dir_entry.setStyleSheet(
            "border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
        )
        self.data_dir_entry.setPlaceholderText("Choose folder")
        self.data_dir_entry.setText(self.user_folder)
        self.data_dir_entry.setEnabled(False)

        self.folder_browser_btn = QPushButton()
        self.folder_browser_btn.setText("Browse")
        self.folder_browser_btn.setStyleSheet(
            "QPushButton {background-color: #97a7b4; border-style: solid; border-color: #97a7b4; border-width: 2px; border-radius: 10px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; font-size: 10pt; font-weight:bold;} "
            + "QPushButton::pressed {background-color: #b5c0c9; border-style: solid; border-color: #b5c0c9; border-width: 2px; border-radius: 10px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; font-size: 10pt; font-weight:bold;}"
        )
        self.folder_browser_btn.setMinimumHeight(37)
        self.folder_browser_btn.setMinimumWidth(80)
        self.folder_browser_btn.setEnabled(False)
        self.folder_browser_btn.clicked.connect(self.choose_save_folder)

        data_dir_layout.addWidget(self.data_dir_entry)
        data_dir_layout.addWidget(self.folder_browser_btn)

        btn_layout = QHBoxLayout()

        # Edit button
        self.primary_btn = QPushButton("Edit")
        self.primary_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.primary_btn.setMinimumHeight(40)
        self.primary_btn.setMinimumWidth(130)
        self.primary_btn.clicked.connect(self.edit_settings)

        # Cancel button
        self.secondary_btn = QPushButton("Cancel")
        self.secondary_btn.setStyleSheet(
            "QPushButton {background-color: #ff0000; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #ff8080; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.secondary_btn.setMinimumHeight(40)
        self.secondary_btn.setMinimumWidth(130)
        self.secondary_btn.clicked.connect(self.close_event)

        btn_layout.addWidget(self.primary_btn, 0, alignment=Qt.AlignmentFlag.AlignRight)
        btn_layout.addWidget(
            self.secondary_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Delete account button
        self.delete_btn = QPushButton(self)
        self.delete_btn.setText("Delete Account")
        self.delete_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff0000;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff8080;}"
        )
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.setMinimumWidth(140)
        self.delete_btn.clicked.connect(self.delete_account)

        # Adding widgets to layout
        main_layout.addWidget(
            self.name_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.name_entry, 0, 1)
        main_layout.addWidget(
            self.acc_bal_label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.acc_bal_entry, 1, 1)
        main_layout.addWidget(
            self.gross_salary_label, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.gross_salary_entry, 2, 1)
        main_layout.addWidget(
            self.net_salary_label, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.net_salary_entry, 3, 1)
        main_layout.addWidget(
            self.avg_expenses_label, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.avg_expenses_entry, 4, 1)
        main_layout.addWidget(
            self.currency_label, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.currency_entry, 5, 1)
        main_layout.addWidget(
            self.data_dir_label, 6, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(data_dir_widget, 6, 1)
        main_layout.addLayout(btn_layout, 7, 0, 1, 2)
        main_layout.addWidget(
            self.delete_btn, 8, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )

    def choose_save_folder(self):
        """
        Method used for selecting user data folder.
        """
        # Pobranie ścieżki pliku wskazanego przez użytkownika
        data_path = QFileDialog.getExistingDirectory(
            self,
            caption="Choose data folder",
            options=QFileDialog.ShowDirsOnly,
        )

        # Zapis pliku, jeżeli wskazano ścieżkę
        if data_path != "":
            self.data_dir_entry.setText(data_path)

    def delete_account(self):
        """
        Method used for deleting all user data form folder choosen by user and platform app folder.
        """
        # Confirmation box
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure u want to delete account?\nThis will permamently delete all your data!",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            # Delete user data
            for file in os.listdir(self.user_folder):
                print(os.path.join(self.user_folder, file))
                os.remove(os.path.join(self.user_folder, file))

            # Delete user data folder
            print(os.path.join(self.user_folder))
            os.rmdir(os.path.join(self.user_folder))

            # Get the user data directory for the application
            settings_dir = user_data_dir(APP_NAME, VERSION)

            # Delete user settings file and app folder
            print(settings_dir)
            print(os.path.join(settings_dir, "user_settings.json"))
            os.remove(os.path.join(settings_dir, "user_settings.json"))
            os.rmdir(os.path.join(settings_dir))

            self.account_deletion.emit()

            # Close app
            QApplication.quit()
        else:
            self.show()

    def edit_settings(self):
        """
        Method used for change widgets editability based on user choice invoked by button.
        """
        if self.active:  # Editable
            self.name_entry.setEnabled(False)
            self.acc_bal_entry.setEnabled(False)
            self.gross_salary_entry.setEnabled(False)
            self.net_salary_entry.setEnabled(False)
            self.avg_expenses_entry.setEnabled(False)
            self.currency_entry.setEnabled(False)
            self.data_dir_entry.setEnabled(False)
            self.folder_browser_btn.setEnabled(False)
            self.primary_btn.setText("Edit")

            self.active = False
        else:  # Non editable
            self.name_entry.setEnabled(True)
            self.acc_bal_entry.setEnabled(True)
            self.gross_salary_entry.setEnabled(True)
            self.net_salary_entry.setEnabled(True)
            self.avg_expenses_entry.setEnabled(True)
            self.currency_entry.setEnabled(True)
            self.data_dir_entry.setEnabled(True)
            self.folder_browser_btn.setEnabled(True)
            self.primary_btn.setText("Save")

            self.active = True

    def close_event(self):
        """
        Close event which sends signal with user settings as dict if something was edited
        """
        send_signal = False

        if self.name_entry.text() != self.username:
            send_signal = True

        if self.acc_bal_entry.text() != self.acc_balance:
            send_signal = True

        if self.gross_salary_entry.text() != self.gross_salary:
            send_signal = True

        if self.net_salary_entry.text() != self.net_salary:
            send_signal = True

        if self.avg_expenses_entry.text() != self.avg_expenses:
            send_signal = True

        if self.currency_entry.currentText() != self.currency:
            send_signal = True

        if self.data_dir_entry.text() != self.user_folder:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = {
                "USER_NAME": self.name_entry.text(),
                "CURRENT_ACCOUNT_BALANCE": float(
                    self.acc_bal_entry.text().replace(",", ".")
                ),
                "MONTHLY_GROSS_SALARY": float(
                    self.gross_salary_entry.text().replace(",", ".")
                ),
                "MONTHLY_NET_SALARY": float(
                    self.net_salary_entry.text().replace(",", ".")
                ),
                "AVERAGE_MONTHLY_EXPENSE": float(
                    self.avg_expenses_entry.text().replace(",", ".")
                ),
                "CURRENCY": self.currency_entry.currentText(),
                "USER_FOLDER": self.data_dir_entry.text(),
                "DEFAULT_VIEW": self.user_settings.get("DEFAULT_VIEW"),
                "DEFAULT_ANALYSIS": self.user_settings.get("DEFAULT_ANALYSIS"),
                "ANALYSIS_AUTO_RUN": self.user_settings.get("ANALYSIS_AUTO_RUN"),
            }

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

        self.destroy()
