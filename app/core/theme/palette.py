from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, Signal

LIGHT = {
    # Operation types
    "income_text": "#0f6e56",   
    "income_pill_bg": "#e1f5ee",
    "income_pill_text": "#085041",
    "expense_text": "#a32d2d", 
    "expense_pill_bg": "#fcebeb",
    "expense_pill_text": "#791f1f",
    "saving_text": "#534ab7",
    "saving_pill_bg": "#eeedfe",
    "saving_pill_text": "#3c3489",
    "investment_text": "#854f0b",
    "investment_pill_bg": "#faeeda",
    "investment_pill_text": "#633806",

    #  Toggle (ActiveToggleDelegate, ToggleSwitch)
    "toggle_on": "#0f6e56",
    "toggle_off": "#b3b3b3",
    "toggle_knob": "#ffffff",

    # Checkbox (CheckboxDelegate)
    "checkbox_border": "#808080",
    "checkbox_border_hover": "#2a82da",
    "checkbox_fill": "#2a82da",
    "checkbox_check": "#ffffff",

    # Text, for delegates painting their own strings
    "text_primary": "#1e1e1e",
    "text_secondary": "#5a5a5a",
    "text_muted": "#808080",
    "text_disabled": "#b3b3b3",
    "danger": "#a32d2d",

    # Surfaces, for delegates painting their own backgrounds
    "surface": "#ffffff",
    "surface_alt": "#f5f5f5",
    "border": "#d9d9d9",
    "separator": "#ededed",

    # Accent
    "accent": "#2a82da",
    "accent_strong": "#1a5fb4",

    # Icons (SvgIcon / LogoWidget {{ICON_COLOR}}
    "icon": "#1e1e1e",
    "icon_muted": "#808080",

    # Fallbacks for missing data
    "category_fallback": "#888780",  
}


DARK = {
    # Operation types 
    "income_text": "#1d9e75",
    "income_pill_bg": "#085041",
    "income_pill_text": "#9fe1cb",
    "expense_text": "#f09595",
    "expense_pill_bg": "#791f1f",
    "expense_pill_text": "#f7c1c1",
    "saving_text": "#afa9ec",
    "saving_pill_bg": "#3c3489", 
    "saving_pill_text": "#cecbf6",
    "investment_text": "#ef9f27",
    "investment_pill_bg": "#633806",
    "investment_pill_text": "#fac775",

    # Toggle
    "toggle_on": "#1d9e75",
    "toggle_off": "#585b70",
    "toggle_knob": "#ffffff",

    # Checkbox
    "checkbox_border": "#585b70",
    "checkbox_border_hover": "#89b4fa",
    "checkbox_fill": "#2a82da",
    "checkbox_check": "#ffffff",

    # Text
    "text_primary": "#cdd6f4",
    "text_secondary": "#a6adc8",
    "text_muted": "#6c7086",
    "text_disabled": "#585b70",
    "danger": "#f09595",

    # Surfaces
    "surface": "#1e1e2e",
    "surface_alt": "#313244",
    "border": "#45475a",
    "separator": "#313244",

    # Accent 
    "accent": "#2a82da",
    "accent_strong": "#89b4fa",

    # Icons
    "icon": "#cdd6f4",
    "icon_muted": "#a6adc8",

    # Fallbacks 
    "category_fallback": "#b4b2a9",
}
class _PaletteSignals(QObject):
    changed = Signal(str)

palette_signals = _PaletteSignals()

class Palette:
    """Theme-aware colour lookup.
    """

    _theme: str = "light"
    _cache: dict[str, QColor] = {}

    @classmethod
    def set_theme(cls, theme: str) -> None:
        """Rebuild the cache for the given theme. Call before the repaint."""
        cls._theme = "dark" if theme == "dark" else "light"
        source = DARK if cls._theme == "dark" else LIGHT
        cls._cache = {k: QColor(v) for k, v in source.items()}
        palette_signals.changed.emit(cls._theme)   

    @classmethod
    def theme(cls) -> str:
        return cls._theme

    @classmethod
    def color(cls, key: str) -> QColor:
        """QColor for a palette key. Raises KeyError on an unknown key"""
        return cls._cache[key]

    @classmethod
    def hex(cls, key: str) -> str:
        """Hex string, for SVG {{ICON_COLOR}} substitution and stylesheet strings."""
        return cls._cache[key].name()

    @classmethod
    def operation(cls, operation_type, variant: str = "text") -> QColor:
        """Colour for an OperationType.

        variant: "text" | "pill_bg" | "pill_text"
        """
        return cls._cache[f"{operation_type.lower()}_{variant}"]

    @classmethod
    def operation_hex(cls, operation_type, variant: str = "text") -> str:
        return cls.operation(operation_type, variant).name()

Palette.set_theme("light")