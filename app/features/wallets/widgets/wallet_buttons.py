# features/wallets/widgets/wallet_button.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class WalletButton(QPushButton):
    """Styled button for wallet cards. Handles its own theming to avoid QSS conflicts."""

    STYLES = {
        "primary": {
            "normal": "background-color: #e8f0fb; color: #1a5fb4; border: 1px solid #bcd4f0;",
            "hover": "background-color: #d4e4f7; color: #1a5fb4; border: 1px solid #bcd4f0;",
            "pressed": "background-color: #bcd4f0; color: #0d4a8a; border: 1px solid #9abde0;",
        },
        "neutral": {
            "normal": "background-color: #f5f5f5; color: #333333; border: 1px solid #d9d9d9;",
            "hover": "background-color: #e8e8e8; color: #333333; border: 1px solid #d9d9d9;",
            "pressed": "background-color: #d9d9d9; color: #1e1e1e; border: 1px solid #bfbfbf;",
        },
        "danger": {
            "normal": "background-color: #fdeaea; color: #c53030; border: 1px solid #f5c6c6;",
            "hover": "background-color: #fad4d4; color: #c53030; border: 1px solid #f5c6c6;",
            "pressed": "background-color: #f5b3b3; color: #8b1a1a; border: 1px solid #e09a9a;",
        },
        "active_card": {
            "normal": "background-color: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.35);",
            "hover": "background-color: rgba(255,255,255,0.35); color: white; border: 1px solid rgba(255,255,255,0.45);",
            "pressed": "background-color: rgba(255,255,255,0.5); color: white; border: 1px solid rgba(255,255,255,0.55);",
        },
        "add_wallet": {
            "base": "border-radius: 12px; font-size: 14px; padding: 14px;",
            "normal": "background-color: transparent; color: #888888; border: 2px solid #d0d0d0;",
            "hover": "background-color: #f5f5f5; color: #555555; border: 2px solid #b0b0b0;",
            "pressed": "background-color: #e0e0e0; color: #333333; border: 2px solid #999999;",
        },
    }

    BASE = "font-size: 11px;"

    def __init__(
        self,
        text: str,
        variant: str = "neutral",
        width: int = 80,
        height: int = 25,
        on_click=None,
        parent=None,
    ):
        super().__init__(text, parent)
        self._variant = variant
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        if on_click:
            self.clicked.connect(on_click)
        self._apply_style()

    def _apply_style(self):
        style = self.STYLES.get(self._variant, self.STYLES["neutral"])
        base = style.get("base", self.BASE)
        self.setStyleSheet(f"""
            QPushButton {{
                {base}
                {style["normal"]}
            }}
            QPushButton:hover {{
                {style["hover"]}
            }}
            QPushButton:pressed {{
                {style["pressed"]}
            }}
        """)

    def set_variant(self, variant: str):
        """Change button style dynamically."""
        self._variant = variant
        self._apply_style()

    def set_on_click(self, on_click=None):
        if on_click:
            self.clicked.disconnect()
            self.clicked.connect(on_click)
