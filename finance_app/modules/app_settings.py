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
        self.user_def_analysis = self.user_settings.get("DEFAULT_ANALYSIS")
        self.user_auto_analysis = self.user_settings.get("ANALYSIS_AUTO_RUN")

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

        # Default section label
        self.default_section_label = QLabel(self)
        self.default_section_label.setText("Default section")
        self.default_section_label.setContentsMargins(15, 0, 15, 0)
        self.default_section_label.setStyleSheet("color: black; font-size: 10pt;")

        # Default section entry
        self.default_section_entry = QComboBox(self)
        self.default_section_entry.setStyleSheet("padding: 5px;")
        self.default_section_entry.addItems(SECTION_LIST.keys())
        self.default_section_entry.view().setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.default_section_entry.setCurrentText(
            self.user_settings.get("DEFAULT_VIEW")
        )

        # Default analysis label
        self.def_analysis_label = QLabel(self)
        self.def_analysis_label.setText("Default analysis view")
        self.def_analysis_label.setContentsMargins(15, 0, 15, 0)
        self.def_analysis_label.setStyleSheet("color: black; font-size: 10pt;")

        # Default analysis entry
        self.def_analysis_entry = QComboBox(self)
        self.def_analysis_entry.setStyleSheet("padding: 5px;")
        self.def_analysis_entry.addItems(ANALYSIS_TYPES)
        self.def_analysis_entry.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.def_analysis_entry.setCurrentText(
            self.user_settings.get("DEFAULT_ANALYSIS")
        )

        # Auto analysis check
        self.auto_analysis_check = QCheckBox(self)
        self.auto_analysis_check.setText(
            "Automatically run analysis on any transaction change?"
        )
        self.auto_analysis_check.setLayoutDirection(Qt.RightToLeft)
        self.auto_analysis_check.setStyleSheet(
            "color: black; font-size: 10pt; spacing:25px;"
        )
        self.auto_analysis_check.setContentsMargins(50, 0, 50, 0)
        self.auto_analysis_check.setChecked(False)
        if self.user_auto_analysis == 1:
            self.auto_analysis_check.setChecked(True)

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
            self.default_section_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.default_section_entry, 0, 1)

        main_layout.addWidget(
            self.def_analysis_label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(self.def_analysis_entry, 1, 1)

        main_layout.addWidget(
            self.auto_analysis_check, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addItem(self.spacer, 3, 0, 1, 2)

        main_layout.addLayout(btn_layout, 4, 0, 1, 2)

    def save_event(self):
        """
        Saving user app settings. It firstly checks if something was edited.
        """
        send_signal = False

        if self.default_section_entry.currentText() != self.user_def_view:
            send_signal = True

        if self.def_analysis_entry.currentText() != self.user_def_analysis:
            send_signal = True

        if int(self.auto_analysis_check.isChecked()) != self.user_auto_analysis:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = self.user_settings

            user_settings_dict["DEFAULT_VIEW"] = (
                self.default_section_entry.currentText()
            )
            user_settings_dict["DEFAULT_ANALYSIS"] = (
                self.def_analysis_entry.currentText()
            )

            user_settings_dict["ANALYSIS_AUTO_RUN"] = int(
                self.auto_analysis_check.isChecked()
            )

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

    def close_event(self):
        """
        Close event which sends signal with user settings as dict if something was edited
        """
        send_signal = False

        if self.default_section_entry.currentText() != self.user_def_view:
            send_signal = True

        if send_signal and not self.active:
            user_settings_dict = self.user_settings

            user_settings_dict["DEFAULT_VIEW"] = (
                self.default_section_entry.currentText()
            )

            with open(self.user_settings_path, "w") as file:
                json.dump(user_settings_dict, file)

            self.update_settings.emit()

        self.destroy()
