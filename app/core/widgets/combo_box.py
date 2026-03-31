from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout


class ComboBox(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        placeholder: str = None,
        values: list = [],
        default_value: str = None,
    ):
        """
        Combo box with placeholder and label of the box.

        Args:
            text (str, optional): text for label. Defaults to None.
            placeholder (str, optional): placeholder for combobox. Defaults to None.
            values (list, optional): list of values for the combobox. Defaults to [].
            default_value (str, optional): default value to combobox. Defaults to None.
        """
        super().__init__()

        self.widget_layout = QVBoxLayout(self)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        self.combo_box = QComboBox(self)
        self.combo_box.insertItems(0, values)

        if default_value is not None:
            self.combo_box.setCurrentText(default_value)

        if placeholder is not None:
            self.combo_box.setPlaceholderText(placeholder)

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.combo_box)

    def get_value(self):
        """get currently selected value"""
        return self.combo_box.currentText()
