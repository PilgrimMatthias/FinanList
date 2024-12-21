from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime
from platformdirs import user_data_dir

from finance_app.config import *


class AppSettings(QWidget):
    """
    App settings window
    """

    # Signals
    update_settings = Signal()

    def __init__(self, parent, user_settings, user_settings_path):
        super().__init__()

        # User data
        self.user_settings = user_settings
        self.user_settings_path = user_settings_path

        self.user_def_view = self.user_settings.get("DEFAULT_VIEW")

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
        self.setWindowTitle("App Settings")

        main_layout = QGridLayout()
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(QSize(550, 375))
        self.setFixedSize(QSize(500, 450))
        self.setLayout(main_layout)
        main_layout.setSpacing(10)

        # Name label
        self.view_label = QLabel(self)
        self.view_label.setText("Default section")
        self.view_label.setContentsMargins(15, 0, 15, 0)
        self.view_label.setStyleSheet("color: black; font-size: 10pt;")

        # Name entry
        self.view_entry = QComboBox(self)
        self.view_entry.setStyleSheet("padding: 5px;")
        self.view_entry.addItems(SECTION_LIST.keys())
        self.view_entry.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view_entry.setCurrentText(self.user_settings.get("DEFAULT_VIEW"))

        # Spacer do layoutu
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        btn_layout = QHBoxLayout()

        # Edit button
        self.primary_btn = QPushButton("Save")
        self.primary_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.primary_btn.setMinimumHeight(40)
        self.primary_btn.setMinimumWidth(130)
        self.primary_btn.clicked.connect(self.save_event)

        # Cancel button
        self.secondary_btn = QPushButton("Close")
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

        # Adding widgets to layout
        main_layout.addWidget(
            self.view_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.view_entry, 0, 1)
        main_layout.addItem(self.spacer, 1, 0, 1, 2)

        main_layout.addLayout(btn_layout, 2, 0, 1, 2)

    def save_event(self):
        """
        Saving user app settings. It firstly checks if something was edited.
        """
        send_signal = False

        if self.view_entry.currentText() != self.user_def_view:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = self.user_settings

            user_settings_dict["DEFAULT_VIEW"] = self.view_entry.currentText()

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

    def close_event(self):
        """
        Close event which sends signal with user settings as dict if something was edited
        """
        send_signal = False

        if self.view_entry.currentText() != self.user_def_view:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = self.user_settings

            user_settings_dict["DEFAULT_VIEW"] = self.view_entry.currentText()

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

        self.destroy()
