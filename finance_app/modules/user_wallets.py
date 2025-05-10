from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime
from platformdirs import user_data_dir

from finance_app.config import *
from finance_app.modules import LineEdit


class UserWallets(QWidget):
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
        self.wallets = self.user_settings.get("WALLETS")

        self.active_folder = self.user_settings.get("USER_FOLDER")

        self.wallet_widgets = []

        print(self.wallets)

        self.today = datetime.today()
        self.active = False

        self.init_ui()

    def init_ui(self):
        """
        Initialization of accounts settings window
        """
        self.setWindowTitle("Wallets")

        main_layout = QGridLayout()
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(QSize(550, 375))
        self.setFixedSize(QSize(500, 450))
        self.setLayout(main_layout)
        main_layout.setSpacing(10)

        # Create User wallets widgets for each wallet
        for user_wallet in self.wallets.keys():
            temp_walet_name_widget = QLabel(self)
            temp_walet_name_widget.setText(user_wallet)
            temp_walet_name_widget.setContentsMargins(15, 0, 15, 0)
            temp_walet_name_widget.setStyleSheet("color: black; font-size: 10pt;")

            temp_wallet_path_widget = LineEdit(
                self, text=self.wallets.get(user_wallet), enabled=False
            )

            if self.user_folder == self.wallets.get(user_wallet):
                temp_activate_btn = QPushButton("Active")
                temp_activate_btn.setProperty("wallet_name", user_wallet)
                temp_activate_btn.setProperty(
                    "wallet_path", self.wallets.get(user_wallet)
                )
                temp_activate_btn.setStyleSheet(
                    "QPushButton {background-color: #566876; border-style: solid; border-color: #566876; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
                    + "QPushButton::pressed {background-color: #899ba9; border-style: solid; border-color: #899ba9; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
                )
                temp_activate_btn.setMinimumHeight(40)
                temp_activate_btn.setMinimumWidth(100)
                temp_activate_btn.setEnabled(False)
                temp_activate_btn.clicked.connect(
                    lambda ch, user_wallet=user_wallet: self.activate_wallet(
                        user_wallet
                    )
                )
            else:
                temp_activate_btn = QPushButton("Activate")
                temp_activate_btn.setProperty("wallet_name", user_wallet)
                temp_activate_btn.setProperty(
                    "wallet_path", self.wallets.get(user_wallet)
                )
                temp_activate_btn.setStyleSheet(
                    "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
                    + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
                )
                temp_activate_btn.setMinimumHeight(40)
                temp_activate_btn.setMinimumWidth(100)
                temp_activate_btn.clicked.connect(
                    lambda ch, user_wallet=user_wallet: self.activate_wallet(
                        user_wallet
                    )
                )

            self.wallet_widgets.append(
                [temp_walet_name_widget, temp_wallet_path_widget, temp_activate_btn]
            )

        # New wallet button
        self.new_wallet_btn = QPushButton("+ New Wallet")
        self.new_wallet_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.new_wallet_btn.setMinimumHeight(40)
        self.new_wallet_btn.setMinimumWidth(180)

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

        # Spacer for bottom
        self.spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Adding widgets to layout
        for index, [
            wallet_name_widget,
            wallet_path_widget,
            temp_activate_btn,
        ] in enumerate(self.wallet_widgets):
            main_layout.addWidget(wallet_name_widget, 1 + index, 0)
            main_layout.addWidget(wallet_path_widget, 1 + index, 1)
            main_layout.addWidget(temp_activate_btn, 1 + index, 2)

        main_layout.addItem(self.spacer, 2 + index, 0, 1, 3)

        main_layout.addWidget(self.new_wallet_btn, 3 + index, 0, 1, 3)
        main_layout.addLayout(btn_layout, 4 + index, 0, 1, 3)

    def activate_wallet(self, wallet_name):
        print("wallet activation {0}".format(wallet_name))

        self.active_folder = self.wallets.get(wallet_name)

        for wallet_widgets in self.wallet_widgets:
            if self.active_folder == wallet_widgets[-1].property("wallet_path"):
                wallet_widgets[-1].setText("Active")
                wallet_widgets[-1].setStyleSheet(
                    "QPushButton {background-color: #566876; border-style: solid; border-color: #566876; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
                    + "QPushButton::pressed {background-color: #899ba9; border-style: solid; border-color: #899ba9; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
                )
                wallet_widgets[-1].setEnabled(False)
            else:
                wallet_widgets[-1].setText("Activate")
                wallet_widgets[-1].setStyleSheet(
                    "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
                    + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
                )
                wallet_widgets[-1].setEnabled(True)

    def edit_settings(self):
        """
        Method used for change widgets editability based on user choice invoked by button.
        """
        if self.active:  # Editable
            for wallet_widgets in self.wallet_widgets:
                for widget in wallet_widgets[:-1]:
                    widget.setEnabled(False)

            self.primary_btn.setText("Edit")

            self.active = False
        else:  # Non editable
            for wallet_widgets in self.wallet_widgets:
                for widget in wallet_widgets[:-1]:
                    widget.setEnabled(True)
            self.primary_btn.setText("Save")

            self.active = True

    def close_event(self):
        """
        Close event which sends signal with user settings as dict if something was edited
        """
        send_signal = False

        if self.user_folder != self.active_folder:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = {
                "USER_NAME": self.user_settings.get("USER_NAME"),
                "CURRENT_ACCOUNT_BALANCE": self.user_settings.get(
                    "CURRENT_ACCOUNT_BALANCE"
                ),
                "MONTHLY_GROSS_SALARY": self.user_settings.get("MONTHLY_GROSS_SALARY"),
                "MONTHLY_NET_SALARY": self.user_settings.get("MONTHLY_NET_SALARY"),
                "AVERAGE_MONTHLY_EXPENSE": self.user_settings.get(
                    "AVERAGE_MONTHLY_EXPENSE"
                ),
                "CURRENCY": self.user_settings.get("CURRENCY"),
                "USER_FOLDER": self.active_folder,
                "DEFAULT_VIEW": self.user_settings.get("DEFAULT_VIEW"),
                "DEFAULT_ANALYSIS": self.user_settings.get("DEFAULT_ANALYSIS"),
                "ANALYSIS_AUTO_RUN": self.user_settings.get("ANALYSIS_AUTO_RUN"),
                "WALLETS": self.user_settings.get("WALLETS"),
            }

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

        self.destroy()

    def closeEvent(self, event):
        """
        Override close event.

        Invoke close event for user settings update
        """
        self.close_event()
