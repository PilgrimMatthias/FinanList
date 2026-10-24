from app.core.app_state import AppState
from PySide6.QtCore import QSettings

class SettingsService:
    ORG = "STASIMAC"
    APP = "FinanList"

    def __init__(self, app_state: AppState):
        self.settings = QSettings(self.ORG, self.APP)
        self.app_state = app_state

    def get_theme(self) -> str:
        return self.settings.value("theme", "light", type=str)

    def set_theme(self, theme: str):
        self.settings.setValue("theme", theme)
        self.app_state.theme_changed.emit(theme)

    def get_remember_last_user(self) -> bool:
        return self.settings.value("remember_last_user", False, type=bool)

    def set_remember_last_user(self, is_remembered:bool):
        self.settings.setValue("remember_last_user", is_remembered)
        if not is_remembered:
            self.clear_last_user_id()

    def get_last_user_id(self) -> int:
        if not self.settings.contains("last_user_id"):
            return None
        return self.settings.value("last_user_id", 1, type=int)
        
    def set_last_user_id(self, id:int) -> int:
        self.settings.setValue("last_user_id", id)

    def clear_last_user_id(self):
        self.settings.remove("last_user_id")

    def get_default_page(self):
        return self.settings.value("default_page", 0, type=int)

    def set_default_page(self, idx:int):
        self.settings.setValue("default_page", idx)

    def get_page_size(self):
        return self.settings.value("page_size", 50, type=int)
        
    def set_page_size(self, n:int):
        self.settings.setValue("page_size", n)
        self.app_state.page_size_changed.emit(n)

    def get_language(self):
        return self.settings.value("language", "en", type=str)

    def set_language(self, lang:str):
        self.settings.setValue("language", lang)

    def get_date_format(self):
        return self.settings.value("date_format", "%d.%m.%Y", type=str)

    def set_date_format(self, format:str):
        self.settings.setValue("date_format", format)