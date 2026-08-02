from PySide6.QtWidgets import (
    QPushButton,
)

# Buttons below this point size get the [size="small"] QSS modifier
SMALL_FONT_THRESHOLD = 9


class PushButton(QPushButton):
    """Application push button.

    By default the button is styled from the theme QSS. The object name is picked
    automatically - `secondaryButton` when `alternate_look` is set, `primaryButton`
    otherwise - so existing call sites keep their intended look without changes.
    Pass `object_name` explicitly for the other variants (`neutralButton`,
    `dangerButton`, or any feature-specific name).

    Pass `legacy_style=True` to fall back to the old inline stylesheet. That path
    honours `bg_color` / `bg_color_clicked` / `font_size` and is needed anywhere the
    colours are computed at runtime rather than fixed by a theme rule.
    """

    def __init__(
        self,
        text="",
        width=140,
        height=40,
        font_size=10,
        bold_font=True,
        bg_color="#4dacff",
        bg_color_clicked="#0085FC",
        alternate_look=False,
        object_name=None,
        legacy_style=False,
        on_click=None,
    ):
        """
        Args:
            text (str, optional): text inside button. Defaults to "".
            width (int, optional): width of button. Defaults to 140.
            height (int, optional): height of button. Defaults to 40.
            font_size (int, optional): font size. Under 9pt the button also gets
                the [size="small"] QSS modifier. Defaults to 10.
            bold_font (bool, optional): bold font - legacy styling only. Defaults to True.
            bg_color (str, optional): normal colour - legacy styling only. Defaults to "#4dacff".
            bg_color_clicked (str, optional): pressed colour - legacy styling only. Defaults to "#0085FC".
            alternate_look (bool, optional): outlined look. Selects `secondaryButton`
                when no object name is given. Defaults to False.
            object_name (str, optional): QSS object name. Auto-derived when omitted.
            legacy_style (bool, optional): use the inline stylesheet instead of QSS.
                Defaults to False.
            on_click (_type_, optional): on click method. Defaults to None.
        """
        super().__init__()

        self._legacy = legacy_style

        if not self._legacy:
            if object_name is None:
                object_name = "secondaryButton" if alternate_look else "primaryButton"
            self.setObjectName(object_name)

            # Size modifier - QSS cannot read the font_size argument, so small
            # buttons are tagged with a property the theme can select on.
            if font_size < SMALL_FONT_THRESHOLD:
                self.setProperty("size", "small")

        self.setText(text)

        if self._legacy:
            self._build_legacy_stylesheets(
                font_size=font_size,
                bold_font=bold_font,
                bg_color=bg_color,
                bg_color_clicked=bg_color_clicked,
                alternate_look=alternate_look,
            )
            self.setStyleSheet(self.enabled_stylesheet)

        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        if on_click:
            self.clicked.connect(on_click)

    # Old inline styling
    def _build_legacy_stylesheets(
        self, font_size, bold_font, bg_color, bg_color_clicked, alternate_look
    ):
        weight = "bold" if bold_font else "normal"

        alternate_btn_style = (
            "background-color: #ffffff; border-style: solid; border-color: {0}; "
            "border-width: 2px; border-radius: 10px; font-size: {1}pt; color:{0}; "
            "font-weight:{2}; padding: 0px;".format(bg_color, font_size, weight)
        )
        alternate_clicked_btn_style = (
            "background-color: {0}; border-style: solid; border-color: {0}; "
            "border-width: 2px; border-radius: 10px; font-size: {1}pt; color:#ffffff; "
            "font-weight:{2};padding: 0px;".format(bg_color_clicked, font_size, weight)
        )
        btn_style = (
            "background-color: {0}; border-style: solid; border-color: {0}; "
            "border-width: 2px; border-radius: 10px; font-size: {1}pt; "
            "font-weight:{2};padding: 0px;".format(bg_color, font_size, weight)
        )
        clicked_btn_style = (
            "background-color: {0}; border-style: solid; border-color: {0}; "
            "border-width: 2px; border-radius: 10px; font-size: {1}pt; "
            "font-weight:{2};padding: 0px;".format(bg_color_clicked, font_size, weight)
        )
        disabled_btn_style = (
            "background-color: #d9d9d9; border-style: solid; border-color: #d9d9d9; "
            "border-width: 2px; border-radius: 10px; font-size: {0}pt; "
            "font-weight:{1};padding: 0px;".format(font_size, weight)
        )

        self.enabled_stylesheet = (
            "QPushButton {"
            + (alternate_btn_style if alternate_look else btn_style)
            + "} "
            + "QPushButton::pressed {"
            + (alternate_clicked_btn_style if alternate_look else clicked_btn_style)
            + "} "
        )
        self.disabled_stylesheet = (
            "QPushButton {"
            + disabled_btn_style
            + "} "
            + "QPushButton::pressed {"
            + disabled_btn_style
            + "} "
        )

    def set_on_click(self, on_click) -> None:
        """set on click method for button"""
        self.clicked.disconnect()
        self.clicked.connect(on_click)

    def set_btn_text(self, text) -> None:
        """set button text"""
        self.setText(text)

    def set_width(self, width: int):
        """Set width for button"""
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

    def set_variant(self, object_name: str):
        """Switch the QSS variant at runtime (no effect on legacy-styled buttons)."""
        if self._legacy:
            return
        self.setObjectName(object_name)
        self._refresh_style()

    def set_enabled(self, enabled: bool):
        """Enable/disable the button.

        Themed buttons rely on `QPushButton#<object_name>:disabled` - re-applying an
        inline stylesheet here would permanently override the QSS.
        """
        self.setEnabled(enabled)

        if self._legacy:
            self.setStyleSheet(
                self.enabled_stylesheet
                if self.isEnabled()
                else self.disabled_stylesheet
            )

    def _refresh_style(self):
        """Force Qt to re-evaluate QSS selectors after a name/property change."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()