from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ChooseBox(QDialog):
    """
    Window which gives opportunity to choose value from calue list and return it
    """

    def __init__(self, values, msg="Choose value!", parent=None):
        """_summary_

        Args:
            values (list): list to combobox
            msg (str, optional): Message for user. Defaults to "Choose value!".
            parent (_type_, optional): Defaults to None.
        """
        super().__init__(parent)

        # Choosen value
        self.selected_value = None

        # Window initialization with widgets
        self.setWindowTitle(msg)

        layout = QVBoxLayout()
        self.label = QLabel(msg)
        layout.addWidget(self.label)

        # Combo box with values list
        self.combo_box = QComboBox()
        self.combo_box.addItems(map(str, values))
        layout.addWidget(self.combo_box)

        # Confirm / Cancel boxes
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Button styllin
        self.button_box.setStyleSheet(
            "QPushButton {background-color: #5AC37D; border-style: solid; border-color: #5AC37D; border-width: 2px; border-radius: 10px; font-size: 11pt; width:80;} "
            + "QPushButton::pressed {background-color: #8fd6a7; border-style: solid; border-color: #8fd6a7; border-width: 2px; border-radius: 10px; font-size: 11pt;width:80px;}"
        )
        self.button_box.setMinimumHeight(30)
        self.button_box.setMinimumWidth(70)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        """
        Accepting user choosen value
        """
        self.selected_value = str(self.combo_box.currentText())
        super().accept()

    def reject(self):
        """
        Canceling window and settting selected value to None.
        """
        self.selected_value = None
        super().reject()
