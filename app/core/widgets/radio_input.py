from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel, QRadioButton, QVBoxLayout


class RadioInput(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        values: list[tuple[str, any]] = [],
        default_value: str = None,
        on_change=None,
    ):
        """
        Radio input with label of the box.

        Args:
            text (str, optional): text for label. Defaults to None.
            values (list, optional): list of values for the radio input. Defaults to [].
            default_value (str, optional): default value to radio input. Defaults to None.
        """
        super().__init__()

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(5)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        self.radio_buttons_layout = QHBoxLayout()

        self.radio_buttons = []
        for value, display_text in values:
            radio_button = QRadioButton(display_text, self)
            radio_button.value = value

            if default_value is not None and value == default_value:
                radio_button.setChecked(True)

            if on_change is not None:
                radio_button.toggled.connect(on_change)

            self.radio_buttons_layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addLayout(self.radio_buttons_layout)

    def get_value(self):
        """get currently selected value"""
        checked_button = [b for b in self.radio_buttons if b.isChecked()]
        return checked_button[0].value if checked_button else None

    def get_data(self):
        """Returns the userData of the currently selected item."""
        checked_button = [b for b in self.radio_buttons if b.isChecked()]
        return checked_button[0].data() if checked_button else None

    def is_filled(self):
        checked_button = [b for b in self.radio_buttons if b.isChecked()]
        return False if len(checked_button) == 0 else True
