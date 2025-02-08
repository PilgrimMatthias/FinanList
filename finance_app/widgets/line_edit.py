from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    def __init__(
        self,
        parent=None,
        text="",
        stylesheet="padding: 5px;",
        enabled=True,
        validator=False,
    ):
        super().__init__()

        # Declare values
        self.text_edit = text
        self.stylesheet = stylesheet
        self.enabled = enabled

        # Set validator
        if validator:
            validator = QDoubleValidator(0, 999999999, 2)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            self.setValidator(validator)
        self.editingFinished.connect(self.on_item_changed)

        # Set parameters
        if self.text_edit:
            self.setText(text)
            self.on_item_changed()

        self.setStyleSheet(stylesheet)
        self.setEnabled(self.enabled)

    def get_number(self):
        """
        Get number from line edit as float.

        Returns:
            float: QLineEdit text as number
        """
        return float(self.text().replace(" ", "").replace(",", "."))

    def on_item_changed(self):
        """
        Number formatter when editing is finished :
        - Thousand separator: space
        - Decimal separator: dot
        """
        item = self.text()
        try:
            # Cast to float
            number = float(item.replace(" ", "").replace(",", "."))
            if number.is_integer():
                formatted_number = f"{int(number):,}".replace(",", " ")
            else:
                formatted_number = f"{number:,.2f}".replace(",", " ").replace(
                    ".", ","
                )  # Format full decimal numbers

            self.setText(formatted_number)
        except ValueError:
            pass  # If it's not a valid integer, do nothing"
