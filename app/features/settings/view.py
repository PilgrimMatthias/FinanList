from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt
from app.core.widgets.line_frames import HLine
from app.core.widgets.buttons import PushButton
from app.core.widgets.combo_box import ComboBox
from app.core.widgets.radio_input import RadioInput
from app.core.widgets.toggle_switch import SwitchInput
from .service import SettingsService
from app.core.app_state import AppState

_THEMES = [["dark", "dark"], ["light", "light"]]
_SECTIONS = [[0, "Dashboard"], [1, "Analysis"], [2, "History"], [3, "Upcoming"], [4, "Investment"], [5, "Upcoming"], [6, "Categories"]]
_ROWS_PER_PAGE = [[50, "50"], [100, "100"], [150, "150"]]
_LANGUAGES = [["en", "English"]]
_DATE_FORMATS = [["%d.%m.%Y", "DD.MM.YYYY"], ["%d-%m-%Y", "DD-MM-YYYY"]]

class SettingsView(QDialog):
    def __init__(self, service: SettingsService, app_state: AppState, parent=None):
        super().__init__(parent)

        self.service = service
        self.app_state = app_state

        self._init_window()

    def _init_window(self):
        self.setFixedSize(450,600)
        self.setObjectName("settingsDialog")

        title_label = QLabel(self)
        title_label.setText("Settings")
        title_label.setObjectName("settingsDialogTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(self)
        subtitle_label.setText("Preferences for the application")
        subtitle_label.setObjectName("settingsDialogSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_hline = HLine()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setObjectName("settingsScrollArea")

        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(5,0,5,0)

        scroll_area.setWidget(settings_widget)

        # Appearance
        appearance_label = QLabel()
        appearance_label.setText("APPEARANCE")
        appearance_label.setObjectName("settingsSectionLabel")

        appearance_hline = HLine()

        self.theme_box = ComboBox(
            values=_THEMES,
            text="Theme",
            default_value=self.service.get_theme(),
            on_change=self._set_theme
        )

        # Startup
        startup_label = QLabel()
        startup_label.setText("STARTUP")
        startup_label.setObjectName("settingsSectionLabel")

        startup_hline = HLine()

        self.remeber_last_user_input = SwitchInput(
            text="Remember last user",
            sub_text="Skip the profile picker next launch",
            default_value=self.service.get_remember_last_user(),
            on_change=self.service.set_remember_last_user,
        )
        self.startup_box = ComboBox(
            values=_SECTIONS,
            text="Open on",
            default_value=self._set_default_section_text(self.service.get_default_page()),
            on_change=self.service.set_default_page
        )

        # Data
        data_label = QLabel()
        data_label.setText("DATA")
        data_label.setObjectName("settingsSectionLabel")

        data_hline = HLine()

        rows_page_box = ComboBox(
            values=_ROWS_PER_PAGE,
            text="Rows per page",
            sub_text="History and Upcoming tables",
            default_value=str(self.service.get_page_size()),
            on_change=self._set_page_size
        )

        # Regional
        regional_label = QLabel()
        regional_label.setText("REGIONAL")
        regional_label.setObjectName("settingsSectionLabel")

        regional_hline = HLine()

        self.language_box = ComboBox(
            values=_LANGUAGES,
            text="Language",
            default_value=[lang[1] for lang in _LANGUAGES if lang[0] == self.service.get_language()][0],
            on_change=self._set_language
        )

        self.date_format_box = ComboBox(
            values=_DATE_FORMATS,
            text="Date format",
            default_value=[date_f[1] for date_f in _DATE_FORMATS if date_f[0] == self.service.get_date_format()][0],
            on_change=self._set_date_format
        )

        bottom_hline = HLine()

        settings_layout.addWidget(appearance_label)
        settings_layout.addWidget(appearance_hline)
        settings_layout.addWidget(self.theme_box)
        settings_layout.addWidget(startup_label)
        settings_layout.addWidget(startup_hline)
        settings_layout.addWidget(self.remeber_last_user_input)
        settings_layout.addWidget(self.startup_box)
        settings_layout.addWidget(data_label)
        settings_layout.addWidget(data_hline)
        settings_layout.addWidget(rows_page_box)
        settings_layout.addWidget(regional_label)
        settings_layout.addWidget(regional_hline)
        settings_layout.addWidget(self.language_box)
        settings_layout.addWidget(self.date_format_box)


        button_widget = QWidget(self)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0,0,0,0)

        cancel_btn = PushButton(
            text = "Close",
            width=80,
            height=30,
            font_size=10,
            object_name="dangerButton",
            on_click=lambda: self.close()
        )

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)


        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 10, 5, 10)

        # Add widgets
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(top_hline)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(bottom_hline)
        main_layout.addWidget(button_widget)
        

    # Helpers
    def _set_default_section_text(self, section_num:int):
        return [section[1] for section in _SECTIONS if section[0] == section_num][0]

    # Setters
    def _set_theme(self):
        self.service.set_theme(self.theme_box.get_value())

    def _set_page_size(self, idx):
        self.service.set_page_size(_ROWS_PER_PAGE[idx][0])

    def _set_language(self):
        selected = self.language_box.get_value()
        lang = [lang[0] for lang in _LANGUAGES if lang[1] == selected][0]
        self.service.set_language(lang)

    def _set_date_format(self):
        selected = self.date_format_box.get_value()
        date_format = [date_f[0] for date_f in _DATE_FORMATS if date_f[1] == selected][0]
        self.service.set_date_format(date_format)