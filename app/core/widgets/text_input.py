from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout


class TextInput(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        placeholder: str = None,
        validate_number=False,
    ):
        """
        Text input widget with label at the top and line edit below.

        Args:
            text (str, optional): label text. Defaults to None.
            placeholder (str, optional): placeholder for combobox. Defaults to None.
            validate_number (bool, optional): validate number after editing is finished?. Defaults to False.
        """
        super().__init__()
        self.validate_number = validate_number

        self.widget_layout = QVBoxLayout(self)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        self.text_input = QLineEdit(self)

        if placeholder is not None:
            self.text_input.setPlaceholderText(placeholder)

        if self.validate_number:
            self._set_number_validator()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.text_input)

    def get_value(self):
        """get value from line edit"""
        if self.validate_number:
            return float(self.text_input.text().replace(" ", "").replace(",", "."))

        return self.text_input.text()

    def clear(self):
        """clear line edit"""
        self.text_input.clear()

    def is_filled(self):
        """check if text input is filled"""
        if self.text_input.text() == "":
            return False
        return True

    def _set_number_validator(self):
        """Set number validator"""
        validator = QDoubleValidator(0, 999999999, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.text_input.setValidator(validator)
        self.text_input.editingFinished.connect(self._on_item_changed)

    def _on_item_changed(self):
        """
        Number formatter when editing is finished :
        - Thousand separator: space
        - Decimal separator: dot
        """
        item = self.text_input.text()
        try:
            # Cast to float
            number = float(item.replace(" ", "").replace(",", "."))
            if number.is_integer():
                formatted_number = f"{int(number):,}".replace(",", " ")
            else:
                formatted_number = f"{number:,.2f}".replace(",", " ").replace(
                    ".", ","
                )  # Format full decimal numbers

            self.text_input.setText(formatted_number)
        except ValueError:
            pass  # If it's not a valid integer, do nothing"
