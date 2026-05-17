from PySide6.QtWidgets import (
    QPushButton,
)


class PushButton(QPushButton):

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
        on_click=None,
    ):
        """
        Push button with alternate colors optionallity

        Args:
            text (str, optional): text inside button. Defaults to "".
            width (int, optional): width of button. Defaults to 140.
            height (int, optional): height of button. Defaults to 40.
            font_size (int, optional): font size. Defaults to 10.
            bold_font (bool, optional): display bold font in buttton?. Defaults to True.
            bg_color (str, optional): color of button in normal state. Defaults to "#4dacff".
            bg_color_clicked (str, optional): color of clicked button. Defaults to "#0085FC".
            alternate_look (bool, optional): display button in alternate look?. Defaults to False.
            on_click (_type_, optional): on click method. Defaults to None.
        """
        super().__init__()

        alternate_btn_style = "background-color: #ffffff; border-style: solid; border-color: {0}; border-width: 2px; border-radius: 10px; font-size: {1}pt; color:{0}; font-weight:{2};".format(
            bg_color, font_size, "bold" if bold_font else "normal"
        )
        alternate_clicked_btn_style = "background-color: {0}; border-style: solid; border-color: {0}; border-width: 2px; border-radius: 10px; font-size: {1}pt; color:#ffffff; font-weight:{2};".format(
            bg_color_clicked, font_size, "bold" if bold_font else "normal"
        )

        btn_style = "background-color: {0}; border-style: solid; border-color: {0}; border-width: 2px; border-radius: 10px; font-size: {1}pt; font-weight:{2};".format(
            bg_color, font_size, "bold" if bold_font else "normal"
        )
        clicked_btn_style = "background-color: {0}; border-style: solid; border-color: {0}; border-width: 2px; border-radius: 10px; font-size: {1}pt; font-weight:{2};".format(
            bg_color_clicked, font_size, "bold" if bold_font else "normal"
        )

        disabled_btn_style = "background-color: {0}; border-style: solid; border-color: {0}; border-width: 2px; border-radius: 10px; font-size: {1}pt; font-weight:{2};".format(
            "#d9d9d9", font_size, "bold" if bold_font else "normal"
        )

        self.enabled_stylesheet = (
            "QPushButton {"
            + (btn_style if not alternate_look else alternate_btn_style)
            + "} "
            + "QPushButton::pressed {"
            + (clicked_btn_style if not alternate_look else alternate_clicked_btn_style)
            + "} "
        )

        self.disabled_stylesheet = (
            "QPushButton {"
            + (disabled_btn_style)
            + "} "
            + "QPushButton::pressed {"
            + (disabled_btn_style)
            + "} "
        )

        self.setText(text)
        self.setStyleSheet(self.enabled_stylesheet)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        if on_click:
            self.clicked.connect(on_click)

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

    def set_enabled(self, enabled: bool):
        self.setEnabled(enabled)

        if self.isEnabled():

            self.setStyleSheet(self.enabled_stylesheet)
        else:
            self.setStyleSheet(self.disabled_stylesheet)
