from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout


class ComboBox(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        placeholder: str = None,
        values: list[tuple[str, any]] = [],
        default_value: str = None,
        on_change=None,
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
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(5)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        self.combo_box = QComboBox(self)
        self.add_items_with_data(items=values)

        if default_value is not None:
            self.combo_box.setCurrentText(default_value)

        if on_change is not None:
            self.combo_box.currentIndexChanged.connect(on_change)

        if placeholder is not None:
            self.combo_box.setPlaceholderText(placeholder)

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.combo_box)

    def add_items_with_data(self, items: list[tuple[str, any]]):
        """items is a list of (display_text, data) tuples."""
        self.combo_box.clear()
        for data, text in items:
            self.combo_box.addItem(text, userData=data)

    def get_value(self):
        """get currently selected value"""
        return self.combo_box.currentText()

    def get_data(self):
        """Returns the userData of the currently selected item."""
        return self.combo_box.currentData()

    def update_items(self, items: list[str]):
        """Update items in combobox"""

        self.combo_box.blockSignals(True)
        self.combo_box.clear()

        self.combo_box.insertItems(0, items)
        self.combo_box.setCurrentText(items[0])
        self.combo_box.blockSignals(False)

    def is_filled(self):
        """check if text input is filled"""
        if self.combo_box.currentText() == "":
            return False
        return True
